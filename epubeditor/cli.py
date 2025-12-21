import argparse
from pathlib import Path
from importlib.metadata import version

from rich.traceback import install
install(show_locals=True)

parser = argparse.ArgumentParser(description="Epub editor - cli tool for editing epub books.")
parser.add_argument('input', nargs = '+', type = str, help = "Input file (book) or directory with books")
parser.add_argument('-P', '--proceed', action = 'store_true', help = "Continue editing after start with argument")

parser.add_argument('-r', '--rename', action = 'store_true', help = "Rename file(s)")
parser.add_argument('-s', '--sort', action = 'store_true', help = "Sort files in folder structure, author/series/book")
parser.add_argument('-m', '--merge', action = 'store_true', help = "Merge books")
parser.add_argument('-j', '--just', action = 'store_true', help = "Just print metadata")

parser.add_argument('-p', '--pretty', choices = ['native', 'xmllint'], default = '', help = "Fix files, make them readable (Works through xmllint)")
parser.add_argument('-R', '--repack', choices = ['zip', '7z'], default = '', type = str, help = "Repack epub file, can help with problem 'bad zip'")
parser.add_argument('-c', '--cover', type = str, help = "Change cover")

metadata_group = parser.add_argument_group('Arguments for editing metadata')
metadata_group.add_argument('--title', type = str, help = 'Set title for book(s)')
metadata_group.add_argument('--author', nargs = '+', type = str, help = 'Set author(s) for book(s)')
metadata_group.add_argument('--series', type = str, help = 'Set series for book(s)')
metadata_group.add_argument('--series-index', type = str, help = 'Set series index for book(s)')
metadata_group.add_argument('--language', nargs = '+', type = str, help ='Set language(s) for book(s)')
metadata_group.add_argument('--generate-sort', action = 'store_true', help = 'Generate sort name (author, title) for book(s)')

parser.add_argument('--script', type = str)
parser.add_argument('--no-subdirs', action = 'store_true', help = "Don't read books from subdirs")
parser.add_argument('--ignore-config', action = 'store_true', help = "Ignore configuration file")

parser.add_argument('--debug', action = 'store_true', help = "Print debug information")
parser.add_argument('--version', action = 'version', version = f'%(prog)s {version('epubeditor')}', help = "Show version")

args = parser.parse_args()

def are_all_flags_false(parser = parser, args = args, exclude=None):
    if exclude is None:
        exclude = []
    
    exclude.append('input')
    exclude.append('no_subdirs')
    exclude.append('ignore_config')
    exclude.append('debug')
    
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
            if args.no_subdirs:
                input_books = list(input_path.glob('*.epub'))
            else:
                input_books = list(input_path.rglob('*.epub'))
            
            if not input_books:
                raise ValueError("There's no epub files in directory!")
            else:
                for book in input_books:
                    if book not in books:
                        books.append(book)
        
        else:
            raise ValueError("There's no such path!")
    return sorted(books)

def main():
    from epubeditor.main import main as start
    start()

if __name__ == "__main__":
    main()
