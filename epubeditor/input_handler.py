from pathlib import Path

from epubeditor.cli import args
from epubeditor.config import no_subdirs, default_path


def inputHandler():
    if args.input:
        Inputs = args.input
    elif default_path is not None:
        Inputs = [default_path]
    else:
        Inputs = ['.']
    
    if args.debug:
        print(Inputs)
    
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
            if no_subdirs:
                input_books = list(input_path.glob('*.epub'))
            else:
                input_books = list(input_path.rglob('*.epub'))
            
            if not input_books:
                raise ValueError("There's no epub files in the directory!")
            else:
                for book in input_books:
                    if book not in books:
                        books.append(book)
        
        else:
            raise ValueError("There's no such path!")
    return sorted(books)