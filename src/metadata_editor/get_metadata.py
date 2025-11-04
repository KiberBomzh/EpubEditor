namespaces = {
    'opf': 'http://www.idpf.org/2007/opf',
    'dc': 'http://purl.org/dc/elements/1.1/'
}


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
            print(f"Title: {titleR}")
        metadataRead['title'] = titleR
    
    if creators:
        authors = []
        for creator in creators:
            authors.append(creator.text)
        if len(authors) > 1:
            if Print:
                print("Authors:")
                for author in authors:
                    print(f"\t{author}")
            metadataRead['authors'] = authors
        else:
            if Print:
                print(f"Author: {authors[0]}")
            metadataRead['author'] = authors[0]
    
    if language:
        if len(language) > 1:
            languageR = []
            for lan in language:
                languageR.append(lan.text)
            if Print:
                print("Language:")
                for lan in languageR:
                    print(f'\t{lan}')
        else:
            languageR = language[0].text
            if Print:
                print(f"Language: {languageR}")
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
                print(f"Series: {seriesR} {series_indexR}")
            
            metadataRead['series'] = seriesR + ' ' + series_indexR
        else:
            if Print:
                print(f"Series: {seriesR}")
    
    if metadata['version'] == '2.0':
        title_sort = metadata['title_sort']
        if title_sort:
            metadataRead['title_sort'] = title_sort[0].get('content')
            if Print:
                print(f'Title, sort: {metadataRead['title_sort']}')
        
        if len(creators) > 1:
            authors_sort = []
            for creator in creators:
                author_sort = creator.get('{' + namespaces['opf'] + '}file-as')
                if author_sort:
                    authors_sort.append(author_sort)
            metadataRead['authors_sort'] = authors_sort
            if Print:
                print('Authors, sort:')
                for author in authors_sort:
                    print(f'\t{author}')
        elif len(creators) == 1:
            author_sort = creators[0].get('{' + namespaces['opf'] + '}file-as')
            if author_sort:
                metadataRead['author_sort'] = author_sort
                if Print:
                    print(f'Author, sort: {metadataRead['author_sort']}')
    elif metadata['version'] == '3.0':
        if title:
            titleId = title[0].get('id')
            file_as = metadata['file-as']
            if file_as:
                if titleId:
                    title_as = None
                    for i, f in enumerate(file_as):
                        if f.get('refines') == '#' + titleId:
                            title_as = file_as.pop(i)
                    if title_as is not None:
                        metadataRead['title_sort'] = title_as.text
                        if Print:
                            print(f'Title, sort: {metadataRead['title_sort']}')
        
                if len(creators) > 1:
                    authors_sort = []
                    for author_as in file_as:
                        authors_sort.append(author_as.text)
                    metadataRead['authors_sort'] = authors_sort
                    if Print:
                        print('Authors, sort:')
                        for author in authors_sort:
                            print(f'\t{author}')
                elif len(creators) == 1:
                    metadataRead['author_sort'] = file_as[0].text
                    if Print:
                        print(f'Author, sort: {metadataRead['author_sort']}')
    
    return metadataRead

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
