# Description
**Before editing your books always backup them!**

**Only for linux!** 

...and Android (Termux)

## Installing
With pip:
```
pip install git+https://github.com/KiberBomzh/EpubEditor
```

Or, if you have uv:
```
uv tool install git+https://github.com/KiberBomzh/EpubEditor
```

## Dependencies

### Python
- lxml
- rich
- prompt_toolkit

### Command line
- xmllint (libxml2-utils)
- zip, unzip
- 7z

## How to use
Just print:
```
epubeditor
```
By default the programm search books in current dirrctory and subdirectories
If you want to open the programm with one particular book use flag `-i`

Open a book or books or directory with books (include all subdirectory)
```
epubeditor -i <path>
```
You, as well, can choose several books, or a book and a directory
```
epubeditor -i <book1> -i <dir> -i <book2>
```
When the programm is running you can input commands. 

Write `help` to see help message

Write `exit` to exit programm

To go back write `..`

### Simple commands
- `rename` - rename books
- `sort` - sort input in directory, needs main directory. Example main/author/series/01.0 - title
- `pretty` - make xml and html files in a book looks pretty
- `just` - just print metadata for book(s)
- `list` - show all current books
- `repack` - repack all books with zip console utility
- `merge` - merge all books (needs at least two books)

### Complex commands
#### `meta`
Open metadata editor, in which you can:
- `print` - print metadata
- `sort` - generate sort names for author(s), title
- `set` - set metadata
	- `title` - set title
	- `author` - set author(s)
	- `series` - set series and series index
	- `language` - set language
- `add` - add metadata
	- `title` - add title
	- `author` - add author(s)
	- `series` - add series and series index
	- `language` - add language(s)
- `rm` - remove metadata
	- `title` - remove title
	- `author` - remove author(s)
	- `series` - remove series and series index
	- `language` - remove language(s)

#### `toc`
Open table of contents editor, commands:
- `ls` - print all elements and their playOrder or id, (num in following commands)
- `show` 'num' - print information about element
- `edit` 'num' - write new data for element (label, content's src)
- `put` 'num1' 'numN' [in/before/after] 'num' - move element(s)
- `rm` 'num1' 'numN' - remove element(s)
- `add` [in/before/after] 'num' - add new element
- `upper` - change case to upper for all elements, run with: 'num1' 'numN' for particular elements
- `lower` - change case to lower
- `capitalize` - change case to capitalize (first letter to uppercase)
- `title` - change case to title (first letter in every single word to uppercase)

#### `open`
Open book (extract all files in temporary folder) for editing. Here you can:
- `save` - don't forget to do it, `exit` and `..` don't save your book!
- `save_as path/to/book.epub` - save a book as
- `chafa path/to/img` - open an image with chafa
- `extract path/to/file` - extract file in current folder
- `merge path/to/main_file number` - merge files, the number is how many files after main_file you want to merge
- `split path/to/file : path/to/file2` - split files, before this you'll need to add a tag <split_file_here/> in those places where you want to split
- `meta` - open metadata editor, for detail look up
- `toc` - open toc editor
- `rm path/to/file1 : path/to/file2` - remove file(s)
- `add path/to/file1 : path/to/file2 :to path/in/book` - add a file
- `rename path/to/file1 : path/to/file2` - rename a file
- `search query` or `search query &replace_to new_value` for search with replacing

>*Search works with lxml and it is searching only in p tags or if there's not p in div*

- open a file in a text editor such as `micro`, `nano`, `vim`, `nvim` or in `bat`. Print `'your editor' 'path/to/file.xhtml`
- `pretty` `[xmllint/native]` - the same as the pretty in simple commands
- `tree` - print a book tree
- `ls` - print all files in a book
- `just_ls` - print all files without formatting
- `script` `script_name` - start script

## Flags and commands
### Commands
- `sort` - do the same as the command `sort`
    - `p`, `--main-path` - choose main path for sort
    - `-t`, `--template` - template for sort, you can use this many time: `-t "{authors}" -t "{series}" -t "{index/_}{title}"`
    - `--keep-empty-folders` - do not remove empty folders

- `rename` - do the same as the command `rename`
    - `-t`, `--template` - template for renaming

- `repack` - do the same as the command `repack`
    - `-a`, `--archiver` [zip/7z] - archiver, by default zip

- `script` `path/to/your/script or script_name`
    - `--clean-body-attributes` - flag for `split_by_titles`
    - `--include-subtitles` - flag for `toc_from_titles`
    - `--only-h` - flag for `toc_from_titles`
    - `--all-h` - flag for `toc_from_titles`

>*Your script must be executable and take one command-line argument.
This argument is a path to a temp directory in which will be extracted your book.
You can do with files whatever you want, after that they wiil be ziped in your book.
There's some examples in scripts.*


- `meta`
    
    *needs at least one argument*
    - `--title` "Title"
    - `--author` "First Author Name" "Second Author Name"
    - `--series` "Series"
    - `--series-index` "1.5"
    - `--language` "lan-one" "lan-two"
    - `--generate-sort` - generate sort names for a title and an author(s)
    - `-j`, `--just` - do the same as the command `just`

- `cover` `path/to/new/cover.jpg` - set new cover for a book (only if there's already cover)
- `pretty` - do the same as the command `pretty`
- `merge` - do the same as the command `merge`

### Other
- `-h`, `--help` - print help
- `-V`, `--version` - print version
- `--no-subdirs` - do **not** include books from subdirectories
- `--ignore-config` - ignore config file
- `--debug` - print debug information

## Config
For information about config open file config_example.toml.
The programm will not create config file on default. You will need to do it yourself

## Tasks
- [x] Metadata editor
- [x] Pretty print for xml, html files written in one line

- [x] Open book
	- [x] Search in book with replace
	- [x] Editing files (with micro, nano, vim and bat)
	- [x] Renaming files
	- [x] Multiple renaming
	- [x] Add new files
	- [x] Delete files
	- [x] Merge and split

- [x] Table of contents editor
- [x] Add support for books with nav.xhtm
- [x] Fast creating TOC from titles

- [x] Books renaming {author - series 01.0, title}
- [x] Multiple metadata editor
- [x] Sorting books in folders: author/series/book
- [x] Changing cover
- [x] Split and merge books
