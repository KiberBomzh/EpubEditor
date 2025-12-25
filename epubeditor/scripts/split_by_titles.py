from lxml import html

from epubeditor.open_book.merge import merge
from epubeditor.open_book.split import main as split
from epubeditor.open_book.functions import get_files_in_spine_order
from epubeditor.prompt_input import input

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

def main(temp_path, console):
    files = get_files_in_spine_order(temp_path)
    
    
    console.print("[green]Which files you want to exclude?[/]")
    exclude = []
    counter = 0
    for file in files:
        if is_it_nav(file):
            exclude.append(file)
            files.remove(file)
            continue
        
        counter += 1
        console.print(f"[dim white]{counter}[/] [cyan]{file.name}[/]")
    
    while True:
        exclude_files_str = input("Exclude (Enter for skip)")
        if exclude_files_str.strip():
            try:
                nums_str = exclude_files_str.split()
                for num_str in nums_str:
                    num = int(num_str)
                    if num <= 0 or num > counter:
                        raise ValueError(f"Not valid number: {num}")
                    
                    index = num - 1
                    exclude.append(files[index])
            except Exception as err:
                console.print(f'[red]{err} try again.[/]')
                nav_exclude = exclude[0]
                exclude.clear()
                exclude.append(nav_exclude)
                continue
        break
    
    for file in exclude:
        if file in files:
            files.remove(file)
    
    main_file = files.pop(0)
    how_many = len(files)
    
    with console.status('[green]split_by_titles[/]'):
        merge(temp_path, main_file, how_many, exclude = exclude)
        
        put_split_tags(main_file)
        
        main_path_str = str(main_file.relative_to(temp_path))
        split(temp_path, main_path_str)
        
        clean_doubled_xml_declarations(temp_path)
