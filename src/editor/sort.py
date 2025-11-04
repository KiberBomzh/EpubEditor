from pathlib import Path
from rich.progress import track

from src.metadata_editor.get_metadata import getMetadata
from src.editor.book_renamer import getRoot

def main(books):
    main_path = input('Input main folder for sort: ')
    if main_path[:2] == '~/':
        main_path = Path.home() / main_path[2:]
    else:
        main_path = Path(main_path).resolve()
    while not main_path.is_dir():
        main_path = input('Not valid folder, try again: ')
        if main_path[:2] == '~/':
            main_path = Path.home() / main_path[2:]
        else:
            main_path = Path(main_path)
    
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
        
        book.replace(new_book_path)
        
        new_books.append(new_book_path)
    return new_books

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
