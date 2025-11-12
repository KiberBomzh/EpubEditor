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
- tree
- bat
- micro

## How to use
Open book or books or directory with books (include all subdirectory)
```
epubeditor <path>
```
You, as well, can choose several books, or book and directory
```
epubeditor <book1> <dir> <book2>
```
When programm is running you can input commands. 

Write `help` to see help message

Write `exit` to exit programm

To go back write `..`

### Simple commands
- `rename` - rename input (author1 & author2 - series 01.0, title)
- `sort` - sort input in directory, needs main directory. Example main/author/series/01.0 - title
- `pretty` - make xml and html files in book looks pretty  needs xmllint
- `just` - just print metadata for book(s)
- `list` - show all current books
- `repack` - repack all books with zip console utility, if you want to repack them with 7z use during start flag -R 7z
### Complex commands
#### `meta`
Open metadata editor, in which you can:
- `print` - print metadata
- `set` - set metadata
	- `title` - set title
	- `author` - set author(s)
	- `series` - set series and series index
	- `language` - set language
	- `sort` - generate sort names for author(s), title
- `add` - add metadata
	- `title` - add title
	- `author` - add author(s)
	- `series` - add series and series index
	- `language` - add language(s)
- `remove` - remove metadata
	- `title` - remove title
	- `author` - remove author(s)
	- `series` - remove series and series index
	- `language` - remove language(s)

#### `open`
Open book (extract all files in temporary folder) for editing. Here you can:
- `save` - don't forget to do it, `exit` and `..` don't save your book!
- `save_as path/to/book.epub` - save book as
- `meta` - open metadata editor, for detail look up
- `search query` or `search query &replace_to new_value` for search with replacing
	*Search works with lxml and it is searching only in p tags or if there's not p in div*
- open file in text editor such as `micro`, `nano`, `vim` or in `bat`. Print `'your editor' 'path/to/file.xhtml`
- `pretty` - the same as the pretty in simple commands
- `tree` - print book tree, needs console tool 'tree'
- `ls` - print all files in book, very usefull for editing with text editor
- `just_ls` - print all files witgout formatting
## Tasks
- [x] Metadata editor
- [x] Pretty print for xml, html files written in one line

- [ ] Open book
	- [x] Search in book with replace
	- [x] Editing files (with micro, nano, vim and bat)
	- [ ] Renaming files
	- [ ] Multiple renaming
	- [ ] mv and cp
	- [ ] Merge and split
	- [ ] Spliting files according to TOC

- [ ] Table of contents editor
	- [ ] Fast creating TOC from h1, h2, h3

- [x] Books renaming {author - series 01.0, title}
- [x] Multiple metadata editor
- [x] Sorting books in folders: author/series/book
- [x] Changing cover


---

*Sorry for my english, i'm not native speaker, so if somethings isn't clear email me kiberbomzh666@gmail.com*
