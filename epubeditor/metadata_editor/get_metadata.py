from zipfile import ZipFile
from lxml import etree
from rich import print

from epubeditor.namespaces import namespaces

def getMetadataRaw(root):
    # Получение метаданных
    metadata = {}
    
    metadata['version'] = root.get('version')
    version = metadata['version']
    
    metadata['metadata'] = root.xpath('//opf:metadata', namespaces=namespaces)[0]
    metadata['title'] = root.xpath('//dc:title', namespaces=namespaces)
    metadata['creators'] = root.xpath('//dc:creator', namespaces=namespaces)
    metadata['language'] = root.xpath('//dc:language', namespaces=namespaces)
    if version == '2.0':
        metadata['series'] = root.xpath('//opf:meta[@name="calibre:series"]', namespaces=namespaces)
        metadata['series_index'] = root.xpath('//opf:meta[@name="calibre:series_index"]', namespaces=namespaces)
        metadata['title_sort'] = root.xpath('//opf:meta[@name="calibre:title_sort"]', namespaces=namespaces)
    elif version == '3.0':
        metadata['series'] = root.xpath('//opf:meta[@property="belongs-to-collection"]', namespaces=namespaces)
        metadata['series_index'] = root.xpath('//opf:meta[@property="group-position"]', namespaces=namespaces)
        metadata['file-as'] = root.xpath('//opf:meta[@property="file-as"]', namespaces=namespaces)
    
    return metadata

def getMetadata(root, Print = False):
    metadata = getMetadataRaw(root)
    metadataRead = {}
    title = metadata['title']
    creators = metadata['creators']
    language = metadata['language']
    series = metadata['series']
    series_index = metadata['series_index']
    
    if title:
        titleR = title[0].text
        if Print:
            print(f"[cyan]Title:[/cyan] {titleR}")
        metadataRead['title'] = titleR
    
    if creators:
        authors = []
        for creator in creators:
            authors.append(creator.text)
        if len(authors) > 1:
            if Print:
                print("[cyan]Authors:[/cyan]")
                for author in authors:
                    print(f"\t{author}")
            metadataRead['authors'] = authors
        else:
            if Print:
                print(f"[cyan]Author:[/cyan] {authors[0]}")
            metadataRead['author'] = authors[0]
    
    if language:
        if len(language) > 1:
            languageR = []
            for lan in language:
                languageR.append(lan.text)
            if Print:
                print("[cyan]Language:[/cyan]")
                for lan in languageR:
                    print(f'\t{lan}')
        else:
            languageR = language[0].text
            if Print:
                print(f"[cyan]Language:[/cyan] {languageR}")
        metadataRead['language'] = languageR
    
    if series:
        if metadata['version'] == '2.0':
            seriesR = series[0].get('content')
        elif metadata['version'] == '3.0':
            seriesR = series[0].text
        metadataRead['series'] = seriesR
        
        if series_index:
            if metadata['version'] == '2.0':
                series_indexR = series_index[0].get('content')
            elif metadata['version'] == '3.0':
                series_indexR = series_index[0].text
            
            if len(series_indexR) == 1:
                series_indexR = f"0{series_indexR}.0"
            elif '.' not in series_indexR:
                series_indexR += ".0"
            elif '.' in series_indexR and len(series_indexR) == 3:
                series_indexR = '0' + series_indexR
            
            if Print:
                print(f"[cyan]Series:[/cyan] {seriesR} {series_indexR}")
            
            metadataRead['series'] = seriesR + ' ' + series_indexR
        else:
            if Print:
                print(f"[cyan]Series:[/cyan] {seriesR}")
    
    if metadata['version'] == '2.0':
        title_sort = metadata['title_sort']
        if title_sort:
            metadataRead['title_sort'] = title_sort[0].get('content')
            if Print:
                print(f'[blue]Title, sort:[/blue] {metadataRead['title_sort']}')
        
        if len(creators) > 1:
            authors_sort = []
            for creator in creators:
                author_sort = creator.get('{' + namespaces['opf'] + '}file-as')
                if author_sort:
                    authors_sort.append(author_sort)
            metadataRead['authors_sort'] = authors_sort
            if Print and authors_sort:
                print('[blue]Authors, sort:[/blue]')
                for author in authors_sort:
                    print(f'\t{author}')
        elif len(creators) == 1:
            author_sort = creators[0].get('{' + namespaces['opf'] + '}file-as')
            if author_sort:
                metadataRead['author_sort'] = author_sort
                if Print:
                    print(f'[blue]Author, sort:[/blue] {metadataRead['author_sort']}')
    elif metadata['version'] == '3.0':
        if title:
            titleId = title[0].get('id')
            file_as = metadata['file-as']
            if file_as:
                if titleId:
                    for f in file_as:
                        if f.get('refines') == '#' + titleId:
                            metadataRead['title_sort'] = f.text
                            if Print:
                                print(f'[blue]Title, sort:[/blue] {metadataRead['title_sort']}')
                            break
        
        if len(creators) > 1:
            file_as = metadata['file-as']
            authors_id = []
            for creator in creators:
                authors_id.append(creator.attrib['id'])
            
            authors_sort = []
            for a_id in authors_id:
                for f in file_as:
                    if f.get('refines') == '#' + a_id:
                        authors_sort.append(f.text)
                        break
            metadataRead['authors_sort'] = authors_sort
            if Print and authors_sort:
                print('[blue]Authors, sort:[/blue]')
                for author in authors_sort:
                    print(f'\t{author}')
        elif len(creators) == 1:
            file_as = metadata['file-as']
            author_id = creators[0].get('id')
            for f in file_as:
                if f.get('refines') == '#' + author_id:
                    metadataRead['author_sort'] = f.text
                    if Print:
                        print(f'[blue]Author, sort:[/blue] {metadataRead['author_sort']}')
                    break
    
    return metadataRead

def get_meta_from_book(book):
    ns = namespaces
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
        meta['index'] = series_index.get('content') if series_index is not None else ''
        meta['sort_title'] = title_sort.get('content') if title_sort is not None else ''
        meta['sort_authors'] = creators_sort

    elif version == '3.0':
        meta['series'] = series.text if series is not None else ''
        meta['index'] = series_index.text if series_index is not None else ''
        meta['sort_title'] = title_sort.text if title_sort is not None else ''
        
        meta['sort_authors'] = []
        for creator in creators_sort:
            cr_text = creator.text
            if cr_text is not None:
                meta['sort_authors'].append(cr_text)

    # приведение всех series_index в один вид (обычно они разные идут в calibre "1.0" в 3.0 версии - "1"
    if meta['index']:
        s_index = meta['index']
        if len(s_index) == 1:
            s_index = f"0{s_index}.0"
        elif '.' not in s_index:
            s_index += ".0"
        elif '.' in s_index and len(s_index) == 3:
            s_index = '0' + s_index
        
        meta['index'] = s_index

    return meta


if __name__ == "__main__":
    print("This is just module, try to run cli.py")
