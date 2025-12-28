from epubeditor.metadata_editor.get_metadata import get_meta_from_book
from epubeditor.open_book.files_operations import get_without_forbidden_chars
from epubeditor.cli import args


debug = args.debug


# все места в которые нужно подставить переменные берутся в фигурные скобки
# всё что после / - это разделитель который добавляется только если в книге есть такая переменная
# указывать его в самом конце

# для languages и authors нужно указать после названия переменной разделитель для переменных
# то есть если указать {authors&} то выйдет следующее: author1 & author2, если автор только один
# ничего добавляться не будет
# если укзать разделителем '1' то будет использован толькл первый элемент, первый автор, первый язык

# '|' - это если нужно заключать текст в какие-то скобки
# обязательно указаывать слева и справа
# то есть, чтоб заключить в () нужно указать (|)
# можно использовать любые разрешенные символы

# можно привязать одну переменную к другой
# например: нужно указывать номер серии только если есть серия
# {series/ <index*/, >}
# дополнительные переменные нужно указывать как конец текущей, то есть после '/'
# сами переменные заключать в < >, после имени переменной указывать '*'
# такие переменные поддерживают всё тоже самое что и обычные
# '|', '/' это всё
# нельзя только привязать ещё переменных к ним
# к основным переменным можно добавлять сколько угодно вложенных


# Значения
# authors - авторы
# series, index - серия, номер в серии
# title - название книги
# languages - язык
# sort_authors, sort_title - сортировочные имена

def unwrap_tag(name, tag, the_var):
    index = name.find(tag)
    if index < 0:
        return name
    
    end_i = name[index:].find('}') + index
    the_tag = name[index + len(tag): end_i]
    
    if debug:
        print('the_var in beginning')
        print(the_tag, '\n')

    
    # проверка есть ли привязанные знаки
    line_index = the_tag.find('/')
    if line_index >= 0:
        bind_text = the_tag[line_index + 1:]
        the_tag = the_tag[:line_index]
    else:
        bind_text = ''


    # проверка есть ли знаки в которые нужно заключить значение
    # берется по одному символу
    # символ слева от '/' будет левым символом
    # символ справа от '/' будет правым
    embrace_index = the_tag.find('|')
    if embrace_index >= 0:
        embrace_left = the_tag[embrace_index - 1]
        embrace_right = the_tag[embrace_index + 1]
        the_tag = the_tag[:embrace_index - 1] + the_tag[embrace_index + 2:]
    else:
        embrace_left = ''
        embrace_right = ''
    
    
    # если переменная список то нужно проверить есть ли разделитель и развернуть переменную
    if isinstance(the_var, list):
        divider = the_tag
        
        if not divider:
            divider = '&'

        if divider == '1' and len(the_var) > 0:
            var_name = the_var[0]
        else: 
            divider = f' {divider} '
            var_name = divider.join(the_var)
    else:
        var_name = the_var
    
    if debug:
        print('In the end')
        print('the_tag: "', the_tag, '"', sep = '')
        print('embrace_left: "', embrace_left, '"', sep = '')
        print('var_name: "', var_name, '"', sep = '')
        print('embrace_right: "', embrace_right, '"', sep = '')
        print('bind_text: "', bind_text, '"', sep = '')
    
    if var_name:
        name = name[:index] + embrace_left + var_name + embrace_right + bind_text + name[end_i + 1:]
    else:
        name = name[:index] + name[end_i + 1:]
    
    if debug:
        print('End name')
        print(name)
        print('\n\n')
    
    return name


def unwrap_secondary_tags(name, meta):
    counter = 0
    while '*' in name:
        if counter > 100:
            break
        start = name.find('<')
        start_tag = start + 1
        end_tag = name[start_tag:].find('*') + start_tag
        tag = name[start_tag:end_tag]
        end = name[start:].find('>') + start
        name = name[:start] + '{' + tag + name[end_tag + 1:end] + '}' + name[end + 1:]
        
        meta_value = meta[tag]
        if tag == 'index':
            meta_value = series_index_templ_handl(meta_value)
        
        
        name = unwrap_tag(name, '{' + tag, meta_value)
        
        counter += 1
    
    return name


def series_index_templ_handl(s_index):
    if not s_index:
        return s_index
    
    
    from epubeditor.config import index_template as template
    if not template:
        return s_index
    
    
    try:
        nums_in_start, divider, nums_in_end = template.split('|')
        nums_in_start = int(nums_in_start)
        nums_in_end = int(nums_in_end)
    except ValueError:
        print('Wrong series_index template!')
        return s_index
    try:
        s_nums_start, s_nums_end = s_index.split('.')
    except ValueError:
        print(s_index)
        return s_index
    if s_nums_start.startswith('0'):
        s_nums_start = s_nums_start[1:]
    if s_nums_end == '0':
        s_nums_end = ''
    
    if len(s_nums_start) < nums_in_start:
        how_many_zeros = nums_in_start - len(s_nums_start)
        s_nums_start = '0' * how_many_zeros + s_nums_start
    
    if len(s_nums_end) < nums_in_end:
        how_many_zeros = nums_in_end - len(s_nums_end)
        s_nums_end = '0' * how_many_zeros + s_nums_end
    
    
    s_index = s_nums_start
    if s_nums_end:
        s_index += divider + s_nums_end
    
    return s_index


def get_name(meta, template):
    name = template
    
    while '{' in name:
        for key, value in meta.items():
            tag = '{' + key
            if tag not in name:
                continue
            
            
            if key == 'index':
                value = series_index_templ_handl(value)
            
            name = unwrap_tag(name, tag, value)
        
        if '*' in name:
            name = unwrap_secondary_tags(name, meta)
    
    if debug:
        print("Before check forbidden chars")
        print(name)
    
    name = get_without_forbidden_chars(name)
    
    if debug:
        print('New name')
        print(name)
    
    return name

def main(book, template):
    meta = get_meta_from_book(book)
    
    if isinstance(template, str):
        template = [template]
    
    names = []
    for templ in template:
        name = get_name(meta, templ)
        if name:
            names.append(name)
    
    if len(names) == 1:
        return names[0]
    
    return names