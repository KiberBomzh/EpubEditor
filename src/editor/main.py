import zipfile
from pathlib import Path
import subprocess
from lxml import etree
import tempfile
from rich.progress import track

from src.metadata_editor import main as metadata_editor
from src.metadata_editor.get_metadata import getMetadata
from src.open_book import main as open_book
from src.open_book.main import zip_errors
from src.editor import cover, book_renamer, sort

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

def repack(book):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        subprocess.run(f'cd "{temp_path}" && unzip "{book}" && zip "{book}" ./*', shell = True)

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
        
        metadata_editor.main(opf)
        
        subprocess.run(f'cd {temp_path} && zip -u "{book}" {opf_relative}', shell = True)

def chooseOption(action, args):
    books = args[0]
    if books:
        match action:
            case "open":
                if len(books) > 1:
                    print("There's more than one book!")
                else:
                    open_book.main(books[0])
            case "meta":
                if len(books) == 1:
                    editOpf(books[0])
                else:
                    print('In developing...')
            case "cover":
                if len(books) == 1:
                    cover.main(books[0])
                else:
                    print("There's more than one book!")
            case "rename":
                books = book_renamer.main(books)
                return books
            case "sort":
                books = sort.main(books)
                return books
            case "pretty":
                if len(books) > 1:
                    for book in track(books, description = "Pretty"):
                        open_book.openBook(book, open_book.toPretty)
                else:
                    open_book.openBook(books[0], open_book.toPretty)
                
                if zip_errors:
                    print('Bad zip file!')
                    for er in zip_errors:
                        print(er)
            case "just":
                justReadMetadata(books)
            case "repack":
                if len(books) > 1:
                    for book in books:
                        repack(book)
                else:
                    repack(books[0])
            case _:
                print("There's no such option, try again.")
    else:
        raise ValueError("There's no such book!")


def main(books: list):
    helpmsg = ("Options:\n" +
        "\t-Open book                    'open'\n" +
        "\t-Edit metadata                'meta'\n" +
        "\t-Change cover                 'cover'\n" +
        "\t-Rename                       'rename'\n" +
        "\t-Sort, author/series/book     'sort'\n" +
        "\t-Pretty                       'pretty'\n" +
        "\t-Just print metadata          'just'\n" +
        "\t-Repack bad zip               'repack'\n" +
        "\t-Exit")
    optList = ['open', 'meta', 'cover', 'rename', 'sort', 'pretty', 'just', 'repack']
    prompt(chooseOption, optList, helpmsg, args = [books])

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
