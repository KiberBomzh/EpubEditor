from zipfile import ZipFile
from lxml import etree
from rich.progress import track

from src.metadata_editor.get_metadata import getMetadata

def getRoot(book):
    with ZipFile(book, 'r') as b_read:
        for file in b_read.namelist():
            if file.endswith('.opf'):
                f_opf = file
        with b_read.open(f_opf) as opf:
            tree = etree.parse(opf)
    return tree.getroot()

#Формат названия: АВТОР - СЕРИЯ НОМЕР_СЕРИИ, НАЗВАНИЕ
def rename(book):
    root = getRoot(book)
    meta = getMetadata(root)
    metaKeys = list(meta.keys())
    
    if 'authors' in metaKeys:
        authors = meta['authors'].pop(0)
        while meta['authors']:
            authors += f" & {meta['authors'].pop(0)}"
        first_block = authors + ' - '
    elif 'author' in metaKeys:
        first_block = f"{meta['author']} - "
    else: 
        first_block = ''
    
    if 'series' in metaKeys:
        second_block = meta['series'] + ', '
    else: 
        second_block = ''
    
    name = first_block + second_block + meta['title']
    
    forbiddenChars = {'<', '>', ':', '"', '/', '|', '?', '*'}
    for char in name:
        if char in forbiddenChars:
            name = name.replace(char, '_')
    
    new_book = book.parent / f'{name}.epub'
    
    if book.name != new_book:
        new_book_path = book.rename(new_book)
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
