import subprocess
import argparse
from pathlib import Path
from rich.progress import track

from src.editor.main import main as editor
from src.editor.main import chooseOption, repack
from src.editor import cover
from src.open_book.main import zip_errors, subprocess_errors
from src.open_book.main import openBook

parser = argparse.ArgumentParser(description="Epub editor")
parser.add_argument('input', nargs = '+', type = str, help = "Input file (book) or directory with books")
parser.add_argument('-P', '--proceed', action = 'store_true', help = "Continue editing after start with argument")

parser.add_argument('-r', '--rename', action = 'store_true', help = "Rename file(s)")
parser.add_argument('-s', '--sort', action = 'store_true', help = "Sort files in fold structure, author/series/book")
parser.add_argument('-p', '--pretty', action = 'store_true', help = "Fix files, make them readable (Works through xmllint)")
parser.add_argument('-j', '--just', action = 'store_true', help = "Just print metadata")

parser.add_argument('-R', '--repack', choices = ['zip', '7z'], default = '', type = str, help = "Repack epub file, can help with problem 'bad zip'")
parser.add_argument('-c', '--cover', type = str, help = "Change cover")

parser.add_argument('--script', type = str)

args = parser.parse_args()

def scriptRun(temp_path):
    subprocess.call([args.script, temp_path])

def are_all_flags_false(parser, args, exclude=None):
    if exclude is None:
        exclude = []
    
    exclude.append('input')
    
    for action in parser._actions:
        if action.dest not in exclude:
            if getattr(args, action.dest, False):
                return False
    return True

def inputHandler(Inputs):
    books = []
    for Input in Inputs:
        input_path = Path(Input).resolve()
        
        if input_path.is_file():
            if input_path.name.endswith('.epub'):
                if input_path not in books:
                    books.append(input_path)
            else:
                raise ValueError("The file isn't epub!")
        
        elif input_path.is_dir():
            input_books = list(input_path.rglob('*.epub'))
            if input_books is None:
                raise ValueError("There's no epub files in directory!")
            else:
                for book in input_books:
                    if book not in books:
                        books.append(book)
        
        else:
            raise ValueError("There's no such path!")
    return books


def argHandler(books):
    if args.repack:
        subprocess_errors.clear()
        repack(books, args.repack)
        if subprocess_errors:
            print('Subprocess Error:')
            for error in subprocess_errors:
                print(error)
    
    if args.just:
        chooseOption('just', [books])
    
    if args.pretty:
        chooseOption('pretty', [books])
    
    if args.cover:
        cover.optionHandl('', [books], cover = args.cover)
    
    if args.proceed:
        editor(books)

    if args.rename:
        books = chooseOption('rename', [books])
    
    if args.sort:
        books = chooseOption('sort', [books])
    
    if args.script:
        subprocess_errors.clear()
        zip_errors.clear()
        
        if len(books) == 1:
            openBook(books[0], scriptRun)
        elif len(books) > 1:
            for book in track(books, description = 'Script'):
                openBook(book, scriptRun)
        
        if subprocess_errors:
            print('Subprocess Error:')
            for error in subprocess_errors:
                print(error)
        
        if zip_errors:
            print('Bad zip file!')
            for er in zip_errors:
                print(er)

def main():
    books = inputHandler(args.input)
    if are_all_flags_false(parser, args):
        editor(books)
    else:
        argHandler(books)


if __name__ == "__main__":
    main()
