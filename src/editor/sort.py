from pathlib import Path
from rich.progress import track
from rich.prompt import Prompt

from src.metadata_editor.get_metadata import getMetadata
from src.editor.book_renamer import getRoot

def main(books):
    # Получение пути к главной папке для сортировки
    main_path = Prompt.ask('[green]Input main folder for sort')
    if main_path[:2] == '~/':
        main_path = Path.home() / main_path[2:]
    else:
        main_path = Path(main_path).resolve()
    while not main_path.is_dir():
        main_path = Prompt.ask('[green]Not valid folder, try again')
        if main_path[:2] == '~/':
            main_path = Path.home() / main_path[2:]
        else:
            main_path = Path(main_path)
    
    # Сама сортировка
    new_books = []
    for book in track(books, description = "Sort"):
        root = getRoot(book)
        meta = getMetadata(root)
        metaKeys = list(meta.keys())
        
        if 'authors' in metaKeys:
            author = meta.get('authors')[0]
        else:
            author = meta['author']
        
        if 'series' in metaKeys:
            new_fold = main_path / author / meta['series'][:-5]
            book_name = meta['series'][-4:] + ' - ' + meta['title'] + '.epub'
        else:
            new_fold = main_path / author
            book_name = meta['title'] + '.epub'
        
        new_book_path = new_fold / book_name
        new_book = str(new_book_path.relative_to(main_path))
        forbiddenChars = {'<', '>', ':', '"', '|', '?', '*'}
        is_forb = False
        for char in forbiddenChars:
            if char in new_book:
                is_forb = True
                break
        if is_forb:
            for char in new_book:
                if char in forbiddenChars:
                    new_book = new_book.replace(char, '_')
            new_book_path = main_path / new_book
        
        if new_book_path in new_books:
            continue
        
        if not new_fold.exists():
            new_fold.mkdir(parents = True)
        
        if book != new_book_path:
            book.replace(new_book_path)
        
        new_books.append(new_book_path)
    
    # Удаление пустых папок
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
                print(f"Empty folder removed: {empty_folder}")
            except OSError as e:
                print(f"Failed to remove {empty_folder}: {e}")
    
    return new_books

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
