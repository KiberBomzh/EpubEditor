from lxml import html

from epubeditor.open_book.merge import merge
from epubeditor.open_book.split import main as split
from epubeditor.open_book.functions import get_files_in_spine_order

from epubeditor.scripts.clean_doubled_xml_declarations import main as clean_doubled_xml_declarations
from epubeditor import config


clean_body_attributes = True

if config:
    if 'scripts' in config:
        if 'split_by_titles' in config['scripts']:
            flags = {}
            for flag in config['scripts']['split_by_titles']:
                flags.update(flag)
            
            if 'clean_body_attributes' in flags:
                clean_body_attributes = flags['clean_body_attributes']


def put_split_tags(file):
    tree = html.parse(file)
    root = tree.getroot()
    
    if clean_body_attributes:
        body = root.find('body')
    
        for attr in reversed(body.attrib.keys()):
            del body.attrib[attr]
    
    h_titles = root.xpath('''
        //h1 |
        //h2 |
        //h3 |
        //h4 |
        //h5 |
        //h6
    ''')
    
    class_titles = root.xpath('''
        //*[@class="title1"] |
        //*[@class="title2"] |
        //*[@class="title3"] |
        //*[@class="title4"] |
        //*[@class="title5"] |
        //*[@class="title6"] |
        //*[@class="title"] |
        //*[@class="book-title"]
    ''')
    
    if h_titles:
        titles = h_titles
    elif class_titles:
        titles = class_titles
    else:
        titles = []
    
    for el in titles:
        split_el = html.Element('split_file_here')
        el.addprevious(split_el)
    
    tree.write(
        file,
        pretty_print = True,
        xml_declaration = True,
        encoding = 'UTF-8'
    )

def is_it_nav(file):
    root = html.parse(file).getroot()
    nav = root.xpath('//nav')
    if nav:
        return True
    else:
        return False

def main(temp_path):
    files = get_files_in_spine_order(temp_path)
    main_file = files.pop(0)
    if is_it_nav(main_file):
        main_file = files.pop(0)
    
    
    exclude = []
    for file in files:
        if is_it_nav(file):
            exclude.append(file)
            files.remove(file)
            break

    how_many = len(files)
    merge(temp_path, main_file, how_many, exclude = exclude)
    
    put_split_tags(main_file)
    
    main_path_str = str(main_file.relative_to(temp_path))
    split(temp_path, main_path_str)
    
    clean_doubled_xml_declarations(temp_path)
