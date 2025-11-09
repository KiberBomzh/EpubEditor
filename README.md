# Description
**Before editing your books always backup them!**

**Only for linux!** 

...and Android (Termux)

## Installing
With pip:

Download latest release [Tap](https://github.com/KiberBomzh/EpubEditor/releases/latest/download/epubeditor-latest-py3-none-any.whl)

Then install .whl file with:
```
pip install epubeditor-latest-py3-none-any.whl
```

Or, if you have uv, just type:
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

## Tasks
- [x] Metadata editor
- [x] Pretty print for xml, html files written in one line

- [ ] In open book
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
- [ ] Multiple metadata editor
- [x] Sorting books in folders: author/series/book
- [x] Changing cover
