from pathlib import Path
import shutil
from rich.progress import track

from epubeditor.editor.template_handler import main as get_name
from epubeditor.config import name_template


def rename(book):
    name = get_name(book, name_template)
    
    if not name:
        print(book.name, "does not have metadata for renaming!")
        return book
    
    new_book = book.parent / f'{name}.epub'
    
    if book != new_book and not new_book.exists():
        new_book_path = Path(shutil.move(book, new_book))
    else:
        new_book_path = book
    return new_book_path


def main(books):
    if not isinstance(books, list):
        books = [books]
    
    new_books = []
    if len(books) > 1:
        for book in track(books, description = "Rename"):
            new_books.append(rename(book))
    else:
        new_books.append(rename(books[0]))
    return new_books

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
