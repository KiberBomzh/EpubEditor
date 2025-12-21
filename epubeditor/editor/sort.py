from pathlib import Path
from rich.progress import track
from rich.console import Console
from prompt_toolkit.completion import PathCompleter

from epubeditor.editor.template_handler import main as get_name
from epubeditor.prompt_input import input
from epubeditor import config

main_path = None
search_empty_folders = True
sort_template = [
    '{authors1}',
    '{series}',
    '{index/ - }{title}'
]

if config:
    if 'sort' in config:
        if 'main_path' in config['sort']:
            main_path = config['sort']['main_path']

        if 'search_empty_folders' in config['sort']:
            search_empty_folders = config['sort']['search_empty_folders']
        
        if 'sort_template' in config['sort']:
            sort_template = config['sort']['sort_template']


def sort(book, main_path):
    main_path = Path('/data/data/com.termux/files/home/testBooks')
    path_parts = get_name(book, sort_template)
    new_book_path = main_path / ('/'.join(path_parts) + '.epub')
    
    
    if not new_book_path.parent.exists():
        new_book_path.parent.mkdir(parents = True)
    
    if book != new_book_path:
        book.replace(new_book_path)
    
    return new_book_path


def rm_empty_folders(main_path):
    console = Console()
    with console.status('[green]Searching empty folders...[/]'):
        removed_any = True
        while removed_any:
            removed_any = False
            empty_folders = []
            for folder in main_path.rglob('*'):
                if folder.is_dir() and not any(folder.iterdir()):
                    empty_folders.append(folder)
            
            for empty_folder in sorted(empty_folders, key = lambda x: len(x.parts), reverse = True):
                try:
                    empty_folder.rmdir()
                    removed_any = True
                    console.log(f"Empty folder removed: {empty_folder}")
                except OSError as e:
                    console.log(f"Failed to remove {empty_folder}: {e}")


def main(books):
    global main_path
    path_completer = PathCompleter(
        expanduser=True,  # Раскрывать ~ в домашнюю директорию
        file_filter=lambda name: '.' != Path(name).stem[0],
        min_input_len=0,  # Показывать сразу
        get_paths=lambda: ['.'],
    )
    
    
    if main_path is None:
        # Получение пути к главной папке для сортировки
        main_path = input('Main folder for sort', completer = path_completer)
    
    if main_path[:2] == '~/':
        main_path = Path.home() / main_path[2:]
    else:
        main_path = Path(main_path).resolve()
    
    
    while not main_path.is_dir():
        main_path = input('Not valid folder, try again: ', completer = path_completer)
        if main_path[:2] == '~/':
            main_path = Path.home() / main_path[2:]
        else:
            main_path = Path(main_path)
    
    # сортировка
    new_books = []
    if len(books) > 1:
        for book in track(books, description = "Sort"):
            new_books.append(sort(book, main_path))
    else:
        new_books.append(sort(books[0], main_path))
    
    if search_empty_folders:
        rm_empty_folders(main_path)
    
    return new_books

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
