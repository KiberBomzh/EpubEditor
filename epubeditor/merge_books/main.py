import tempfile
import zipfile
from pathlib import Path
from rich.console import Console
from lxml import etree

from epubeditor.merge_books.get_data_from_user import get_order, get_new_book
from epubeditor.merge_books.create_meta import create_opf, create_toc, create_container
from epubeditor.merge_books.cp_meta import cp_opf, cp_toc
from epubeditor.metadata_editor.multiple_editor import getMetaFromUser
from epubeditor.metadata_editor.create_sort import createSort
from epubeditor.namespaces import namespaces as ns


console = Console()


def cp_files(main_temp_path, main_opf, main_toc, book, num):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        with zipfile.ZipFile(book, 'r') as book_read:
            try:
                book_read.extractall(temp_path)
            except zipfile.BadZipFile as err:
                console.log(err)
                return
            
        from epubeditor.editor.main import getOpf, getToc
        
        container = temp_path / 'META-INF/container.xml'
        opf = temp_path / getOpf(container)
        toc_tuple_str, what_is_it = getToc(opf)
        toc = (opf.parent / toc_tuple_str[0]).resolve()
        
        
        exclude_files = [opf, toc, (temp_path / 'mimetype')]
        files = []
        for file in temp_path.rglob('*'):
            file_rel = file.relative_to(temp_path)
            if (
                not any(part == 'META-INF' for part in file_rel.parts)
                and file not in exclude_files
                and file.is_file()
            ):
                files.append(file)
        
        # Путь для добавления файлов из этой книги в главную
        num_path = main_temp_path / str(num)
        num_path.mkdir()
        
        cp_opf(main_opf, opf, num, temp_path) 
        cp_toc(main_toc, toc, what_is_it, num, temp_path)
        
        for file in files:
            new_file = (num_path / file.relative_to(temp_path))
            new_file.parent.mkdir(exist_ok = True, parents = True)
            file.replace(new_file)

def create_id_and_order_in_toc(toc):
    tree = etree.parse(toc)
    root = tree.getroot()
    
    # nav_map = root.find('ncx:navMap', namespaces = ns)
    points = root.xpath('//ncx:navPoint', namespaces = ns)
    counter = 1
    for point in points:
        point.attrib['playOrder'] = str(counter)
        point.attrib['id'] = f'id-{counter}'
        
        counter += 1
    
    
    tree.write(
        toc,
        pretty_print = True,
        xml_declaration = True,
        encoding = 'UTF-8'
    )

def gen_sort_names(opf, generate_sort):
    tree = etree.parse(opf)
    root = tree.getroot()
    
    if generate_sort:
        createSort(root)
    
    
    tree.write(
        opf,
        pretty_print = True,
        xml_declaration = True,
        encoding = 'UTF-8'
    )

def main(books):
    try:
        print('Order:')
        books = get_order(books)
        new_book = get_new_book()
        new_meta, generate_sort = getMetaFromUser()
    except EOFError:
        return
    
    with console.status('[green]Merging...[/]'):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Создание обязательных файлов
            m_type = temp_path / 'mimetype'
            m_type.touch()
            m_type.write_text('application/epub+zip')
            
            create_container(temp_path)
            
            
            # Создание opf и toc
            opf = create_opf(temp_path, new_meta)
            toc = create_toc(temp_path, new_meta['title'])
            
            
            counter = 1
            for book in books:
                cp_files(
                    temp_path,
                    opf,
                    toc,
                    book,
                    counter
                )
                counter += 1
            
            create_id_and_order_in_toc(toc)
            # Шлифонуть для внешнего вида, плюс обработка generate_sort
            gen_sort_names(opf, generate_sort)
            
            # Запись всех файлов из temp_path в new_book
            with zipfile.ZipFile(new_book, 'w') as book_w:
                for file in temp_path.rglob('*'):
                    if file.is_file():
                        arcname = file.relative_to(temp_path).as_posix()
                        book_w.write(file, arcname)
