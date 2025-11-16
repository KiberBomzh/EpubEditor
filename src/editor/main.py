import zipfile
import sys
from pathlib import Path
import subprocess
from lxml import etree
import tempfile
from rich.progress import track
from rich.prompt import Confirm, Prompt
from rich.console import Console

from src.metadata_editor import main as metadata_editor
from src.metadata_editor.get_metadata import getMetadata
from src.metadata_editor.multiple_editor import main as multipleEditor
from src.open_book import main as open_book
from src.open_book.main import zip_errors, subprocess_errors
from src.editor import cover, book_renamer, sort
from src.toc.main import main as tocEditor

from src.console_prompt import main as prompt

def justReadMetadata(books):
    for book in books:
        with zipfile.ZipFile(book, 'r') as book_r:
            for file in book_r.namelist():
                if file.endswith('.opf'):
                    opf_file = file
            with book_r.open(opf_file) as opf:
                tree = etree.parse(opf)
                getMetadata(tree.getroot(), Print = True)
        
        if books[-1] != book:
            print('\n', end='')

def repack(books, with_what = 'zip'):
    if len(books) > 1:
        for book in track(books, description = 'Repack'):
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                if with_what == 'zip':
                    result = subprocess.run(f'cd "{temp_path}" && unzip -q "{book}" ; zip -q "{book}" ./*', shell = True, capture_output = True, text = True)
                elif with_what == '7z':
                    result = subprocess.run(f'cd "{temp_path}" && 7z x "{book}" -y -bso0 -bsp0 ; 7z a "{book}" ./* -y -bso0 -bsp0', shell = True, capture_output = True, text = True)
            
            if result.stderr:
                subprocess_errors.append(f"--------------------\n{book}\n{result.stderr}")
            else:
                print(f'Reapcked: {book}')
    elif len(books) == 1:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            if with_what == 'zip':
                result = subprocess.run(f'cd "{temp_path}" && unzip -q "{books[0]}" ; zip -q "{books[0]}" ./*', shell = True, capture_output = True, text = True)
            elif with_what == '7z':
                result = subprocess.run(f'cd "{temp_path}" && 7z x "{books[0]}" -y -bso0 -bsp0 ; 7z a "{books[0]}" ./* -y -bso0 -bsp0', shell = True, capture_output = True, text = True)
        
        if result.stderr:
            subprocess_errors.append(f"--------------------\n{books[0]}\n{result.stderr}")
        else:
            print(f'Reapcked: {books[0]}')

def editOpf(book):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        with zipfile.ZipFile(book, 'r') as book_r:
            for file in book_r.namelist():
                if file.endswith('.opf'):
                    opf_file = file
            book_r.extract(opf_file, temp_path)
        
        opf = list(temp_path.rglob('*.opf'))[0]
        opf_relative = opf.relative_to(temp_path)
        
        act = metadata_editor.main(opf)
        subprocess.run(f'cd {temp_path} && zip -u "{book}" {opf_relative}', shell = True)
        return act

def editToc(book):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        with zipfile.ZipFile(book, 'r') as book_r:
            for file in book_r.namelist():
                if file.endswith('.opf'):
                    opf_file = file
                elif file.endswith('.ncx'):
                    ncx_file = file
            book_r.extract(opf_file, temp_path)
            book_r.extract(ncx_file, temp_path)
        
        ncx = list(temp_path.rglob('*.ncx'))
        if len(ncx) == 1:
            toc = ncx[0]
        else:
            print("Error during geting .ncx file!")
            return
        
        opf_f = list(temp_path.rglob('*.opf'))
        if len(opf_f) == 1:
            opf = opf_f[0]
        else:
            print("Error during geting .opf file!")
            return
        toc_relative = toc.relative_to(temp_path)
        opf_relative = opf.relative_to(temp_path)
        
        act = tocEditor(toc, opf)
        subprocess.run(f'cd {temp_path} && zip -u "{book}" {toc_relative} {opf_relative}', shell = True)
        return act

def open_books(books):
    for index, book in enumerate(books):
        parent = book.parent.relative_to(book.parent.parent)
        console.print(f'[magenta]{index + 1}[/] [dim]{parent}/[/]{book.name}')
    
    choice = int(Prompt.ask('[green]Choose what book you want to open'))
    while choice > len(books):
        choice = int(Prompt.ask('[green]Number is too big, try again'))
    
    return open_book.main(books[choice - 1])

console = Console()

def chooseOption(action, args):
    books = args[0]
    
    if books:
        match action:
            case "open":
                if len(books) > 1:
                    if len(books) > 100:
                        if Confirm.ask(f'[green]Show all({len(books)}) books?[/]'):
                            
                            if open_books(books) == 'exit':
                                sys.exit()
                    else:
                        
                        if open_books(books) == 'exit':
                            sys.exit()
                else:
                    if open_book.main(books[0]) == 'exit':
                        sys.exit()
            case "meta":
                if len(books) == 1:
                    if editOpf(books[0]) == 'exit':
                        sys.exit()
                else:
                    multipleEditor(books)
            case "toc":
                if len(books) == 1:
                    if editToc(books[0]) == 'exit':
                        sys.exit()
                else:
                    print("There's more than one book!")
            case "cover":
                if len(books) == 1:
                    if cover.main(books[0]) == 'exit':
                        sys.exit()
                else:
                    print("There's more than one book!")
            case "rename":
                books = book_renamer.main(books)
                return books
            case "sort":
                books = sort.main(books)
                return books
            case "pretty":
                zip_errors.clear()
                subprocess_errors.clear()
                if len(books) > 1:
                    for book in track(books, description = "Pretty"):
                        print('--------------------')
                        print(book)
                        open_book.openBook(book, open_book.toPretty, [book])
                else:
                    open_book.openBook(books[0], open_book.toPretty)
                
                if subprocess_errors:
                    print('Subprocess Error:')
                    for error in subprocess_errors:
                        print(error)
                
                if zip_errors:
                    print('Bad zip file!')
                    for er in zip_errors:
                        print(er)
            case "just":
                justReadMetadata(books)
            case "list":
                for book in books:
                    print(book)
            case "repack":
                subprocess_errors.clear()
                repack(books)
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
        "\t-Just print metadata          [green]'just'[/]\n" +
        "\t-Print current books          [green]'list'[/]\n" +
        "\t-Repack bad zip               [green]'repack'[/]\n" +
        "\t-Exit")
    optList = ['open', 'meta', 'toc', 'cover', 'rename', 'sort', 'pretty', 'just', 'list', 'repack']
    prompt(chooseOption, optList, helpmsg, args = [books])

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
