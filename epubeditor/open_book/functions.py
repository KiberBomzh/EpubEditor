import os
from rich import print
from rich.tree import Tree
from lxml import etree
from epubeditor.namespaces import namespaces as ns

def get_files_in_spine_order(temp_path):
    from epubeditor.editor.main import getOpf
    
    container = temp_path / 'META-INF/container.xml'
    opf = temp_path / getOpf(container)
    root = etree.parse(opf).getroot()
    
    manifest = root.find('opf:manifest', namespaces = ns)
    spine = root.find('opf:spine', namespaces = ns)
    
    files = []
    for itemref in spine.xpath('./opf:itemref', namespaces = ns):
        ref = itemref.get('idref')
        item = manifest.find(f'opf:item[@id="{ref}"]', namespaces = ns)
        file = opf.parent / item.get('href')
        files.append(file.resolve())
    
    return files

def get_separator(word, color = ''):
    columns, lines = os.get_terminal_size()
    len_word = len(word)
    empty_space = columns - len_word
    left_part_len = empty_space // 2
    right_part_len = columns - (left_part_len + len_word)
    
    char = '-'
    left_part = char * left_part_len
    right_part = char * right_part_len
    
    
    separator = left_part + word + right_part
    if color:
        separator = f'[{color}]{separator}[/]'
    
    return separator

def sort_and_paint_files(files, path, separators = False, files_in_order = []):
    book_content = []
    for file in files_in_order:
        book_content.append(f'[green]{file.relative_to(path)}[/]')
    
    css = []
    images = []
    fonts = []
    other = []
    opf = ''
    ncx = ''
    for file in sorted(files):
        f = file.relative_to(path)
        match file.suffix.lower():
            case '.xhtml' | '.html' | '.htm':
                book_content.append(f'[green]{f}[/]')
            case '.jpg' | '.jpeg' | '.png' | '.gif':
                images.append(f'[magenta]{f}[/]')
            case '.ttf' | '.otf':
                fonts.append(f'[dark_orange]{f}[/]')
            case '.css':
                css.append(f'[blue]{f}[/]')
            case '.opf':
                opf = f'[yellow]{f}[/]'
            case '.ncx':
                ncx = f'[cyan]{f}[/]'
            case _:
                other.append(f'[dim]{f}[/]')
    
    new_files = []
    
    if opf:
        if separators:
            separator = get_separator('INFO', color = 'yellow')
            new_files.append(separator)
        new_files.append(opf)
    
    if ncx:
        new_files.append(ncx)
    
    if book_content and separators:
        separator = get_separator('HTML', color = 'green')
        new_files.append(separator)
    for f in book_content:
        new_files.append(f)
    
    if css and separators:
        separator = get_separator('CSS', color = 'blue')
        new_files.append(separator)
    for f in css:
        new_files.append(f)
    
    if fonts and separators:
        separator = get_separator('FONTS', color = 'dark_orange')
        new_files.append(separator)
    for f in fonts:
        new_files.append(f)
    
    if images and separators:
        separator = get_separator('IMAGES', color = 'magenta')
        new_files.append(separator)
    for f in images:
        new_files.append(f)
    
    if other and separators:
        separator = get_separator('OTHER', color = 'dim')
        new_files.append(separator)
    for f in other:
        new_files.append(f)
    
    return new_files

def tree_rec(path, branch):
    folders = []
    files = []
    for subpath in path.glob('*'):
        if subpath.is_dir():
            folders.append(subpath)
        elif subpath.is_file():
            files.append(subpath)
    
    for fold in sorted(folders):
        subbranch = branch.add(f'{fold.relative_to(path)}')
        tree_rec(fold, subbranch)
    
    new_files = sort_and_paint_files(files, path)
    for file in new_files:
        branch.add(file)

def tree(temp_path, book_name):
    book_tree = Tree(book_name)
    folders = []
    files = []
    for path in temp_path.glob('*'):
        if path.is_dir():
            folders.append(path)
        elif path.is_file():
            files.append(path)
    
    for fold in sorted(folders):
        branch = book_tree.add(f'{fold.relative_to(temp_path)}')
        tree_rec(fold, branch)
    
    new_files = sort_and_paint_files(files, temp_path)
    for file in new_files:
        book_tree.add(file)
    
    print(book_tree)

def ls(temp_path, separators = True):
    files_in_so = get_files_in_spine_order(temp_path)
    files = []
    for file in temp_path.rglob('*'):
        if file.is_file() and file not in files_in_so:
            files.append(file)
    
    
    new_files = sort_and_paint_files(
        files, 
        temp_path, 
        separators = separators,
        files_in_order = files_in_so
    )
    
    for f in new_files:
        print(f)