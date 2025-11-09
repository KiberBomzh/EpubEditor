import subprocess
from rich.progress import track

from src.editor.main import main as editor
from src.editor.main import chooseOption, repack
from src.editor import cover
from src.open_book.main import zip_errors, subprocess_errors
from src.open_book.main import openBook
from src.cli import args, are_all_flags_false, inputHandler

def scriptRun(temp_path):
    subprocess.call([args.script, temp_path])

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
    books = inputHandler()
    if are_all_flags_false():
        editor(books)
    else:
        argHandler(books)

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
