import zipfile
import sys
from pathlib import Path
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor

from lxml import etree
from rich.progress import track
from rich.prompt import Confirm, Prompt
from rich.console import Console
from prompt_toolkit.completion import NestedCompleter

from epubeditor.metadata_editor import main as metadata_editor
from epubeditor.metadata_editor.get_metadata import getMetadata
from epubeditor.metadata_editor.multiple_editor import main as multipleEditor
from epubeditor.open_book import main as open_book
from epubeditor.open_book.main import zip_errors, subprocess_errors
from epubeditor.editor import cover, book_renamer, sort
from epubeditor.toc.main import main as tocEditor
from epubeditor.merge_books.main import main as merge
from epubeditor.namespaces import namespaces as ns

from epubeditor.console_prompt import main as prompt


console = Console()

def justReadMetadata(books):
    for book in books:
        console.print(f'[dim white]{book.parent.name}/[/][blue]{book.name}[/]')
        with zipfile.ZipFile(book, 'r') as book_r:
            with book_r.open('META-INF/container.xml') as container:
                opf_file = getOpf(container)
            
            with book_r.open(opf_file) as opf:
                tree = etree.parse(opf)
                getMetadata(tree.getroot(), Print = True)
        
        if books[-1] != book:
            print('\n', end='')

def repack_book(book, with_what):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        if with_what == 'zip':
            result = subprocess.run(f'cd "{temp_path}" && unzip -q "{book}" ; zip -q "{book}" ./*', shell = True, capture_output = True, text = True)
        elif with_what == '7z':
            result = subprocess.run(f'cd "{temp_path}" && 7z x "{book}" -y -bso0 -bsp0 ; 7z a "{book}" ./* -y -bso0 -bsp0', shell = True, capture_output = True, text = True)
    
    return result, f'Reapcked: {book.parent.name}/{book.name}'

def repack(books, with_what = 'zip'):
    if len(books) > 1:
        with ThreadPoolExecutor(max_workers = 5) as executor:
            works = []
            for book in books:
                works.append(executor.submit(repack_book, book, with_what))
            
            for work in track(works, description = 'Repack'):
                result, current_book = work.result()
                if result.stderr:
                    subprocess_errors.append(f"--------------------\n{book}\n{result.stderr}")
                # else:
                #     print(current_book)
    elif len(books) == 1:
        result, book_msg = repack_book(books[0], with_what)
        if result.stderr:
            subprocess_errors.append(f"--------------------\n{books[0]}\n{result.stderr}")
        # else:
        #     console.print(book_msg)

def if_element(elements, error_msg, raise_error = True):
    if elements:
        return elements[0]
    else:
        if raise_error:
            raise TypeError(error_msg)
        else:
            return None

def getOpf(container):
    root = etree.parse(container).getroot()
    full_path = root.xpath(
        '//n:rootfiles/n:rootfile/@full-path',
        namespaces = {'n': 'urn:oasis:names:tc:opendocument:xmlns:container'}
    )
    opf_file = if_element(full_path, 'Cannot get .opf file!')
    
    return opf_file

def getToc(opf):
    root = etree.parse(opf).getroot()
    toc_id = if_element(
        root.xpath('//opf:spine/@toc', namespaces = ns),
        'Toc id is not found!'
    )
    
    toc = if_element(
        root.xpath(f'//opf:manifest/opf:item[@id="{toc_id}"]/@href', namespaces = ns),
        'Toc path is not found!',
        raise_error = False
    )
    if toc is not None:
        nav = if_element(
            root.xpath('//opf:manifest/opf:item[@properties="nav"]/@href', namespaces = ns),
            'Nav path is not found!',
            raise_error = False
        )
        
        if nav is not None:
            return (toc, nav), 'toc and nav'
    
    else:
        nav = if_element(
            root.xpath('//opf:manifest/opf:item[@properties="nav"]/@href', namespaces = ns),
            'Nav path is not found!'
        )
        return (nav,), 'nav'
    
    return (toc,), 'toc'

def editOpf(book):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        with zipfile.ZipFile(book, 'r') as book_r:
            with book_r.open('META-INF/container.xml') as container:
                opf_file = getOpf(container)
            
            book_r.extract(opf_file, temp_path)
        
        opf = temp_path / opf_file
        opf_relative = opf.relative_to(temp_path)
        
        act = metadata_editor.main(opf, books = [book])
        subprocess.run(f'cd {temp_path} && zip -u "{book}" {opf_relative}', shell = True)
        return act

def editToc(book):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        with zipfile.ZipFile(book, 'r') as book_r:
            with book_r.open('META-INF/container.xml') as container:
                opf_file = getOpf(container)
            
            with book_r.open(opf_file) as opf_r:
                toc_tuple_str, what_is_it = getToc(opf_r)
            
            nav_file = None
            match what_is_it:
                case 'toc' | 'nav':
                    toc_file = toc_tuple_str[0]
                case 'toc and nav':
                    toc_file = toc_tuple_str[0]
                    nav_file = toc_tuple_str[1]
            
            t_index = toc_file.rfind('/') + 1
            for f in book_r.namelist():
                if toc_file[t_index:] in f:
                    toc_file = f
            
            if nav_file is not None:
                t_index = nav_file.rfind('/') + 1
                for f in book_r.namelist():
                    if nav_file[t_index:] in f:
                        nav_file = f
                
                book_r.extract(nav_file, temp_path)
            
            book_r.extract(opf_file, temp_path)
            book_r.extract(toc_file, temp_path)
        
        toc = temp_path / toc_file
        if not toc.is_file():
            print("Error during geting .ncx file!")
            return
        
        opf = temp_path / opf_file
        if not opf.is_file():
            print("Error during geting .opf file!")
            return
        
        toc_relative = toc.relative_to(temp_path)
        opf_relative = opf.relative_to(temp_path)
        
        if nav_file is not None:
            nav = temp_path / nav_file
            if not nav.is_file():
                print("Error during geting nav file!")
                return
            
            nav_relative = nav.relative_to(temp_path)
            
            toc_tuple = (toc, nav)
            
            act = tocEditor(toc_tuple, opf, what_is_it, books = [book])
            subprocess.run(f'cd {temp_path} && zip -u "{book}" {toc_relative} {nav_relative} {opf_relative}', shell = True)
            return act
        
        toc_tuple = (toc,)
        act = tocEditor(toc_tuple, opf, what_is_it, books = [book])
        subprocess.run(f'cd {temp_path} && zip -u "{book}" {toc_relative} {opf_relative}', shell = True)
        return act

def open_books(books):
    for index, book in enumerate(books):
        console.print(f'[magenta]{index + 1}[/] [dim]{book.parent.name}/[/][blue]{book.name}[/]')
    
    choice = int(Prompt.ask('[green]Choose what book you want to open'))
    while choice > len(books) or choice <= 0:
        choice = int(Prompt.ask('[green]Not valid number, try again'))
    
    return open_book.main(books[choice - 1])

def get_choosen_book(books, sec_arg):
    choosen_book = None
    for book in books:
        if book.stem.strip() == sec_arg.strip():
            choosen_book = book
            break
    
    if choosen_book is None:
        print(f"There's no such book: '{sec_arg}'!")
        return None
    return choosen_book

def chooseOption(action, args):
    books = args[0]
    sec_arg = ''
    if len(args) > 1:
        sec_arg = args[1]
    
    if books:
        match action:
            case "open":
                if len(books) > 1 and not sec_arg:
                    if len(books) > 100:
                        if Confirm.ask(f'[green]Show all({len(books)}) books?[/]'):
                            
                            if open_books(books) == 'exit':
                                sys.exit()
                    else:
                        
                        if open_books(books) == 'exit':
                            sys.exit()
                elif len(books) > 1 and sec_arg:
                    choosen_book = get_choosen_book(books, sec_arg)
                    if choosen_book is None:
                        return
                    
                    if open_book.main(choosen_book) == 'exit':
                        sys.exit()
                else:
                    if open_book.main(books[0]) == 'exit':
                        sys.exit()
            case "meta":
                if len(books) == 1:
                    if editOpf(books[0]) == 'exit':
                        sys.exit()
                elif len(books) > 1 and sec_arg:
                    choosen_book = get_choosen_book(books, sec_arg)
                    if choosen_book is None:
                        return
                    
                    if editOpf(choosen_book) == 'exit':
                        sys.exit()
                else:
                    multipleEditor(books)
            case "toc":
                if len(books) == 1:
                    if editToc(books[0]) == 'exit':
                        sys.exit()
                elif len(books) > 1 and sec_arg:
                    choosen_book = get_choosen_book(books, sec_arg)
                    if choosen_book is None:
                        return
                    
                    if editToc(choosen_book) == 'exit':
                        sys.exit()
                else:
                    print("There's more than one book!")
            case "cover":
                if len(books) == 1:
                    if cover.main(books[0]) == 'exit':
                        sys.exit()
                elif len(books) > 1 and sec_arg:
                    choosen_book = get_choosen_book(books, sec_arg)
                    if choosen_book is None:
                        return
                    
                    if cover.main(choosen_book) == 'exit':
                        sys.exit()
                else:
                    print("There's more than one book!")
            case "rename":
                args[0] = book_renamer.main(books)
                return args[0]
            case "sort":
                args[0] = sort.main(books)
                return args[0]
            case "pretty":
                zip_errors.clear()
                subprocess_errors.clear()
                if len(books) > 1:
                    with ThreadPoolExecutor(max_workers = 3) as executor:
                        works = []
                        for book in books:
                            works.append(executor.submit(open_book.openBook, book, open_book.toPretty, [book]))
                        
                        for work in track(works, description = "Pretty"):
                            work.result()
                        
                else:
                    with console.status("[green]Pretty...[/]"):
                        open_book.openBook(books[0], open_book.toPretty, [books[0]])
                
                if subprocess_errors:
                    print('Subprocess Error:')
                    for error in subprocess_errors:
                        print(error)
                
                if zip_errors:
                    print('Bad zip file!')
                    for er in zip_errors:
                        print(er)
            case "merge":
                if len(books) > 1:
                    merge(books)
                else:
                    print("There's ony one book!")
            case "just":
                justReadMetadata(books)
            case "ls":
                for book in books:
                    console.print(f"[dim]{book.parent.name}/[/][blue]{book.name}[/]")
            case "repack":
                subprocess_errors.clear()
                repack(
                    books, 
                    with_what = args[1] if len(args) > 1 else 'zip'
                )
                if subprocess_errors:
                    print('Subprocess Error:')
                    for error in subprocess_errors:
                        print(error)
            case _:
                print("There's no such option, try again.")
    else:
        raise ValueError("There's no such book!")


def main(books: list):
    helpmsg = ("Options:\n" +
        "\t-Open book                    [green]'open'[/]\n" +
        "\t-Edit metadata                [green]'meta'[/]\n" +
        "\t-Edit table of contents       [green]'toc'[/]\n" +
        "\t-Change cover                 [green]'cover'[/]\n" +
        "\t-Rename                       [green]'rename'[/]\n" +
        "\t-Sort, author/series/book     [green]'sort'[/]\n" +
        "\t-Pretty                       [green]'pretty'[/]\n" +
        "\t-Merge books                  [green]'merge'[/]\n" +
        "\t-Just print metadata          [green]'just'[/]\n" +
        "\t-Print current books          [green]'ls'[/]\n" +
        "\t-Repack bad zip               [green]'repack'[/]\n" +
        "\t-Exit")
    
    if len(books) > 1:
        compl_books = {}
        for book in books:
            compl_books[book.stem] = None
    else:
        compl_books = None
    
    completer = NestedCompleter.from_nested_dict({
        'open': compl_books,
        'meta': compl_books,
        'toc': compl_books,
        'cover': compl_books,
        'rename': None,
        'sort': None,
        'pretty': None,
        'merge': None,
        'just': None,
        'ls': None,
        'repack': {'zip': None, '7z': None},
        'help': None,
        'exit': None
    })
    prompt(chooseOption, completer, helpmsg, args = [books])

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
