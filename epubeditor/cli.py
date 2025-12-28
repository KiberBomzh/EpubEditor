import argparse
from importlib.metadata import version

parser = argparse.ArgumentParser(description="Epub editor - cli tool for editing epub books.")
parser.add_argument('-i', '--input', action = 'append', default = [], help = "Input files (books) or directories with books")
parser.add_argument('-V', '--version', action = 'version', version = f'%(prog)s {version('epubeditor')}', help = "Show version")
parser.add_argument('--debug', action = 'store_true', help = "Print debug information")

parser.add_argument('--no-subdirs', action = 'store_true', help = "Don't read books from subdirs")
parser.add_argument('--ignore-config', action = 'store_true', help = "Ignore configuration file")


subparsers = parser.add_subparsers(dest = 'command', help = "Commands")

sort_parser = subparsers.add_parser('sort', help = "Sort books in folders structure")
sort_parser.add_argument('-p', '--main-path', type = str, help = "Main path for sort")
sort_parser.add_argument('-t', '--template', action = 'append', type = str, default = [], help = "Template for sort")
sort_parser.add_argument('--keep-empty-folders', action = 'store_true', help = "Do NOT remove epty folders in main path")


rename_parser = subparsers.add_parser('rename', help = "Rename file(s)")
rename_parser.add_argument('-t', '--template', type = str, default = '', help = "Template for renaming")


repack_parser = subparsers.add_parser('repack', help = "Repack epub files, can help with problem 'bad zip'")
repack_parser.add_argument('-a', '--archiver', choices = ['zip', '7z'], default = 'zip', type = str, help = "Archiver, zip or 7z")


cover_parser = subparsers.add_parser('cover', help = "Change cover")
cover_parser.add_argument('new_cover', type = str, help = "Path to new cover")


script_parser = subparsers.add_parser('script', help = "Start script")
script_parser.add_argument('script_name', type = str, help = "One from default scripts or path to your script")
script_parser.add_argument('--clean-body-attributes', action = 'store_true', help = "Flag for the split_by_titles script")
script_parser.add_argument('--include-subtitles', action = 'store_true', help = "Flag for the toc_from_titles script")
script_parser.add_argument('--only-h', action = 'store_true', help = "Flag for the toc_from_titles script")
script_parser.add_argument('--all-h', action = 'store_true', help = "Flag for the toc_from_titles script")


meta_parser = subparsers.add_parser('meta', help = "Fast editing metadata")
meta_parser.add_argument('--title', type = str, help = 'Set title for book(s)')
meta_parser.add_argument('--author', nargs = '+', type = str, help = 'Set author(s) for book(s)')
meta_parser.add_argument('--series', type = str, help = 'Set series for book(s)')
meta_parser.add_argument('--series-index', type = str, help = 'Set series index for book(s)')
meta_parser.add_argument('--language', nargs = '+', type = str, help ='Set language(s) for book(s)')
meta_parser.add_argument('--generate-sort', action = 'store_true', help = 'Generate sort name (author, title) for book(s)')

meta_parser.add_argument('-j', '--just', action = 'store_true', help = "Just print metadata")


pretty_parser = subparsers.add_parser('pretty', help = "Fix files, make them readable (Works with xmllint)")
merge_parser = subparsers.add_parser('merge', help = "Merge books")


args = parser.parse_args()


if args.debug:
    from rich.traceback import install
    install(show_locals=True)


def main():
    from epubeditor.main import main as start
    start()

if __name__ == "__main__":
    main()
