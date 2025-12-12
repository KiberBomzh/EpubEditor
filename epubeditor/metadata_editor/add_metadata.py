from lxml import etree
from rich import print

from epubeditor.namespaces import namespaces
from epubeditor.metadata_editor.get_metadata import getMetadataRaw
from epubeditor.prompt_input import input

def print_help():
    print(
        "Available options:",
        "\t-Title, [green]'title'[/]",
        "\t-Author, [green]'author'[/]",
        "\t-Series, [green]'series'[/]",
        "\t-Language, [green]'language'[/]",
        sep = '\n'
    )

def addTitle(metadata, new_title):
    title = etree.Element('{' + namespaces['dc'] + '}title')
    title.text = new_title
    if metadata['version'] == '3.0':
        Id = f'titleId-{len(metadata['title']) + 1}'
        title.set('id', Id)
        IdR = '#' + Id
        title_type = etree.Element('{' + namespaces['opf'] + '}meta')
        title_type.set('refines', IdR)
        title_type.set('property', 'title-type')
        title_type.text = 'main'
        metadata['metadata'].append(title_type)
    metadata['metadata'].insert(0, title)

def addAuthor(root, metadata, new_author):
    creator = etree.Element('{' + namespaces['dc'] + '}creator')
    if metadata['version'] == '2.0':
        creator.set('{' + namespaces['opf'] + '}role', 'aut')
    elif metadata['version'] == '3.0':
        Id = 'authorId'
        count = len(metadata['creators'])
        thisId = root.xpath(f'//dc:creator[@id="{Id}"]', namespaces = namespaces)
        while thisId:
            Id += f'-{count + 1}'
            thisId = root.xpath(f'//dc:creator[@id="{Id}"]', namespaces = namespaces)
        creator.set('id', Id)
    creator.text = new_author
    
    # Добавление автора в разное место в зависимости от того какие элементы уже есть
    if metadata['creators']:
        last_creator = metadata.get('creators')[-1]
        last_creator.addnext(creator)
    elif metadata['title']:
        metadata.get('title')[-1].addnext(creator)
    else:
        metadata['metadata'].insert(0, creator)
    
    if metadata['version'] == '3.0':
        IdR = '#' + Id
        
        aut_role = etree.Element('{' + namespaces['opf'] + '}meta')
        aut_role.set('refines', IdR)
        aut_role.set('property', 'role')
        aut_role.set('scheme', 'marc:relators')
        aut_role.text = 'aut'
        metadata['metadata'].append(aut_role)

def addSeries(metadata, new_series):
    series = etree.Element('{' + namespaces['opf'] + '}meta')
    if metadata['version'] == '2.0':
        series.set('name', 'calibre:series')
        series.set('content', new_series)
    elif metadata['version'] == '3.0':
        series.set('id', 'seriesId')
        series.set('property', 'belongs-to-collection')
        series.text = new_series
        
        collection_type = etree.Element('{' + namespaces['opf'] + '}meta')
        collection_type.set('refines', '#seriesId')
        collection_type.set('property', 'collection-type')
        collection_type.text = 'series'
        metadata['metadata'].append(collection_type)
        
    metadata['metadata'].append(series)

def addSeriesIndex(metadata, new_series_index):
    series_index = etree.Element('{' + namespaces['opf'] + '}meta')
    if metadata['version'] == '2.0':
        series_index.set('name', 'calibre:series_index')
        series_index.set('content', new_series_index)
    elif metadata['version'] == '3.0':
        series_index.set('refines', '#seriesId')
        series_index.set('property', 'group-position')
        series_index.text = new_series_index
    metadata['metadata'].append(series_index)

def addLanguage(root, metadata, new_language):
    firstMeta = root.xpath('//opf:meta', namespaces=namespaces)[0]
    language = etree.Element('{' + namespaces['dc'] + '}language')
    language.text = new_language
    firstMeta.addprevious(language)

def main(action, root):
    metadata = getMetadataRaw(root)
    
    match action:
        case "title":
            if metadata['title']:
                print("Title already exists. Try set title")
            else:
                metadata = getMetadataRaw(root)
                title = input("Title")
                addTitle(metadata, title)
        case "author": 
            metadata = getMetadataRaw(root)
            author = input("Author")
            addAuthor(root, metadata, author)
        case "series":
            metadata = getMetadataRaw(root)
            if metadata['series']:
                print('Series already exists. Try set series')
            else:
                new_series = input("Series")
                addSeries(metadata, new_series)
                
            if not metadata['series_index']:
                new_series_index = input('Series index')
                addSeriesIndex(metadata, new_series_index)
        case "language":
            metadata = getMetadataRaw(root)
            new_language = input('Language')
            addLanguage(root, metadata, new_language)
        case "help":
            print_help()
        case _:
            print("Unknown option for add, try 'add help'")

if __name__ == "__main__":
    print("This is just module, try to run cli.py")