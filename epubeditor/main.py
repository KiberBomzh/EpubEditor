import subprocess
from rich.progress import track
from rich import print

from epubeditor.editor.main import main as editor
from epubeditor.editor.main import chooseOption, repack
from epubeditor.editor import cover
from epubeditor.open_book.main import zip_errors, subprocess_errors
from epubeditor.open_book.main import openBook
from epubeditor.metadata_editor.multiple_editor import main as multipleEditor
from epubeditor.cli import args
from epubeditor.open_book.scripts import main as scripts
from epubeditor.open_book.scripts import scripts_list
from epubeditor import books


def cmd_repack():
    subprocess_errors.clear()
    
    repack(books, args.archiver)
    
    if subprocess_errors:
        print('Subprocess Error:')
        for error in subprocess_errors:
            print(error)


def cmd_metadata():
    if args.just:
        chooseOption('just', [books])
    
    meta_args = ['title', 'author', 'series', 'series_index', 'language', 'generate_sort']
    if any(getattr(args, arg, False) for arg in meta_args):
        new_meta = {}
        new_meta['title'] = args.title
        new_meta['author'] = args.author
        new_meta['series'] = args.series
        new_meta['series_index'] = args.series_index
        new_meta['language'] = args.language
        multipleEditor(books, new_meta, args.generate_sort)
    elif not args.just:
        print("[red]Command meta needs at least one option![/]")


def cmd_script():
    subprocess_errors.clear()
    zip_errors.clear()
    
    def scriptRun(temp_path):
        subprocess.call([args.script_name, temp_path])
    
    
    if len(books) == 1:
        if args.script_name in scripts_list:
            openBook(books[0], scripts, [args.script_name])
        else:
            openBook(books[0], scriptRun)
    elif len(books) > 1:
        if args.script_name in scripts_list:
            for book in track(books, description = 'Script'):
                openBook(book, scripts, [args.script_name])
        else:
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


def argHandler():
    match args.command:
        case 'sort':
            chooseOption('sort', [books])
        
        case 'rename':
            chooseOption('rename', [books])
        
        case 'repack':
            cmd_repack()
        
        case 'cover':
            for book in books:
                cover.optionHandl('', [book], cover = args.new_cover)
        
        case 'meta':
            cmd_metadata()
        
        case 'script':
            cmd_script()
        
        case 'merge':
            chooseOption('merge', [books])
        
        case 'pretty':
            chooseOption('pretty', [books])
        
        case _:
            print("[red]There's no such command![/]")


def main():
    if args.command:
        argHandler()
    else:
        editor(books)

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
