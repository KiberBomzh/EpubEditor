from lxml import etree
import subprocess
import zipfile
import tempfile
from pathlib import Path
from rich.prompt import Prompt

from src.metadata_editor import get_metadata, remove_metadata
from src.metadata_editor.create_sort import createSort
from src.metadata_editor.add_metadata import addTitle, addAuthor, addSeries, addSeriesIndex, addLanguage

def changeOpf(book, func, args = []):
    from src.editor.main import getOpf
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        with zipfile.ZipFile(book, 'r') as book_r:
            with book_r.open('META-INF/container.xml') as container:
                opf_file = getOpf(container)
            
            book_r.extract(opf_file, temp_path)
        
        opf = list(temp_path.rglob('*.opf'))[0]
        opf_relative = opf.relative_to(temp_path)
        
        if args:
            func(opf, args)
        else:
            func(opf)
        
        subprocess.run(f'cd {temp_path} && zip -u "{book}" {opf_relative}', shell = True)

def removeElements(root, metadata, key):
    for el in metadata[key]:
        if metadata['version'] == '3.0' and key in ['title', 'creators']:
            remove_metadata.removeRefines(el, metadata['metadata'], root)
        metadata['metadata'].remove(el)

def changeMetadata(opf, args):
    new_meta = args[0]
    generate_sort = args[1]
    
    tree = etree.parse(opf)
    root = tree.getroot()
    metadata = get_metadata.getMetadataRaw(root)
    
    for key, value in new_meta.items():
        if key == 'author':
            mkey = 'creators'
        else:
            mkey = key
        
        if metadata.get(mkey) and value:
            removeElements(root, metadata, mkey)
        
        if value:
            match key:
                case 'title':
                    addTitle(metadata, value)
                
                case 'author':
                    for author in value:
                        metadata = get_metadata.getMetadataRaw(root)
                        addAuthor(root, metadata, author)
                
                case 'series':
                    addSeries(metadata, value)
                
                case 'series_index':
                    addSeriesIndex(metadata, value)
                
                case 'language':
                    for language in value:
                        addLanguage(root, metadata, language)
    
    if generate_sort:
        createSort(root)
    
    tree.write(opf, encoding='utf-8', xml_declaration = True, pretty_print = True)

def getMetaFromUser():
    new_meta = {}
    title = Prompt.ask('[green]Title')
    author = Prompt.ask('[green]Author')
    series = Prompt.ask('[green]Series')
    series_index = Prompt.ask('[green]Series index')
    language = Prompt.ask('[green]Language')
    choice = Prompt.ask(
        '[green]Generate sort names?',
        choices = ['y', 'n'],
        default = 'n',
        show_choices = True,
        show_default = True
    )
    
    new_meta['title'] = title if title else None
    new_meta['author'] = author.split(' & ') if author else None
    new_meta['series'] = series if series else None
    new_meta['series_index'] = series_index if series_index else None
    new_meta['language'] = language.split(' ') if language else None
    generate_sort = False if choice == 'n' else True
    
    return new_meta, generate_sort

def main(books, new_meta = {}, generate_sort = False):
    if not new_meta:
        new_meta, generate_sort = getMetaFromUser()
    
    for book in books:
        changeOpf(book, changeMetadata, [new_meta, generate_sort])

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
