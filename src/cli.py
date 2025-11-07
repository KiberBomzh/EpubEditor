import argparse
from pathlib import Path

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

def are_all_flags_false(parser = parser, args = args, exclude=None):
    if exclude is None:
        exclude = []
    
    exclude.append('input')
    
    for action in parser._actions:
        if action.dest not in exclude:
            if getattr(args, action.dest, False):
                return False
    return True

def inputHandler(Inputs = args.input):
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

def main():
    from src.main import main as start
    start()

if __name__ == "__main__":
    main()
