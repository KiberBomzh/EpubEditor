from zipfile import ZipFile
from lxml import etree
from rich.progress import track

from epubeditor.namespaces import namespaces as ns
from epubeditor import config

# все места в которые нужно подставить переменные берутся в фигурные скобки
# всё что после | - это разделитель который добавляется только если в книге есть такая переменная
# для languages и authors нужно указать после названия переменной разделитель для переменных
# то есть если указать {authors&} то выйдет следующее: author1 & author2, если автор только один
# ничего добавляться не будет

name_template = '{authors&| - }{series| }{series_index|, }{title}'

if config:
    if 'sort' in config:
        if 'template' in config['sort']:
            name_template = config['sort']['template']                    

# Значения
# authors - авторы
# series, series_index - серия, номер в серии
# title - название книги
# languages - язык
# sort_authors, sort_title - сортировочные имена

def get_meta(book):
    with ZipFile(book, 'r') as b_read:
        for file in b_read.namelist():
            if file.endswith('.opf'):
                f_opf = file
        with b_read.open(f_opf) as opf:
            root = etree.parse(opf).getroot()

    version = root.get('version')
    meta = root.find('opf:metadata', namespaces = ns)
    title = meta.find('dc:title', namespaces = ns)
    creators = meta.findall('dc:creator', namespaces = ns)
    languages = meta.findall('dc:language', namespaces = ns)

    if version == '2.0':
        series = meta.find('opf:meta[@name="calibre:series"]', namespaces = ns)
        series_index = meta.find('opf:meta[@name="calibre:series_index"]', namespaces = ns)
        title_sort = meta.find('opf:meta[@name="calibre:title_sort"]', namespaces = ns)
        
        creators_sort = []
        for creator in creators:
            a_sort = creator.get('{%s}file-as' % ns['opf'])
            if a_sort is not None:
                creators_sort.append(a_sort)

    elif version == '3.0':
        series = meta.find('opf:meta[@property="belongs-to-collection"]', namespaces = ns)
        series_index = meta.find('opf:meta[@property="group-position"]', namespaces = ns)
        
        t_id = title.get('id')
        if t_id is not None:
            title_sort = meta.find(f'opf:meta[@property="file-as"][@refines="#{t_id}"]', namespaces = ns)
        else:
            title_sort = None
        
        creators_sort = []
        for creator in creators:
            c_id = creator.get('id')
            if c_id is not None:
                creator_sort = meta.find(f'opf:meta[@property="file-as"][@refines="#{c_id}"]', namespaces = ns)
                if creator_sort is not None:
                    creators_sort.append(creator_sort)


    meta = {}
    meta['title'] = title.text if title is not None else ''
    meta['authors'] = []
    for creator in creators:
        meta['authors'].append(creator.text)
    
    meta['languages'] = []
    for lang in languages:
        meta['languages'].append(lang.text)
    
    if version == '2.0':
        meta['series'] = series.get('content') if series is not None else ''
        meta['series_index'] = series_index.get('content') if series_index is not None else ''
        meta['sort_title'] = title_sort.get('content') if title_sort is not None else ''
        meta['sort_authors'] = creators_sort

    elif version == '3.0':
        meta['series'] = series.text if series is not None else ''
        meta['series_index'] = series_index.text if series_index is not None else ''
        meta['sort_title'] = title_sort.text if title_sort is not None else ''
        
        meta['sort_authors'] = []
        for creator in creators_sort:
            cr_text = creator.text
            if cr_text is not None:
                meta['sort_authors'].append(cr_text)

    # приведение всех series_index в один вид (обычно они разные идут в calibre "1.0" в 3.0 версии - "1"
    s_index = meta['series_index']
    if len(s_index) == 1:
        s_index = f"0{s_index}.0"
    elif '.' not in s_index:
        s_index += ".0"
    elif '.' in s_index and len(s_index) == 3:
        s_index = '0' + s_index
    
    meta['series_index'] = s_index

    return meta

def unwrap_tag(name, tag, the_var):
    index = name.find(tag)
    if index < 0:
        return name

    end_i = name[index:].find('}') + index
    the_tag = name[index + len(tag): end_i]

    # проверка есть ли привязанные знаки
    line_index = the_tag.find('|')
    if line_index >= 0:
        bind_text = the_tag[line_index + 1:]
    else:
        bind_text = ''

    # если переменная список то нужно проверить есть ли разделитель и развернуть переменную
    if isinstance(the_var, list):
        if line_index < 0:
            divider = the_tag
        else:
            divider = the_tag[:line_index]
        
        if not divider:
            divider = '&'

        divider = f' {divider} '
        var_name = divider.join(the_var)
    else:
        var_name = the_var

    name = name[:index] + var_name + bind_text + name[end_i + 1:] 
    return name


#Формат названия: АВТОР - СЕРИЯ НОМЕР_СЕРИИ, НАЗВАНИЕ
def rename(book):
    meta = get_meta(book)
    
    name = name_template
    for key, value in meta.items():
        tag = '{' + key
        name = unwrap_tag(name, tag, value)
    
    forbiddenChars = {'<', '>', ':', '"', '/', '|', '?', '*'}
    for char in name:
        if char in forbiddenChars:
            name = name.replace(char, '_')
    
    new_book = book.parent / f'{name}.epub'
    
    if book.name != new_book:
        new_book_path = book.rename(new_book)
    else:
        new_book_path = book
    return new_book_path

def main(books):
    if not isinstance(books, list):
        books = [books]
    
    new_books = []
    if len(books) > 1:
        for book in track(books, description = "Rename"):
            new_books.append(rename(book))
    else:
        new_books.append(rename(books[0]))
    return new_books

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
