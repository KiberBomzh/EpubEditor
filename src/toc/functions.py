from rich.tree import Tree
from rich import print
from prompt_toolkit import prompt as input
from lxml import etree
import random

from src.console_prompt import style
from src.namespaces import namespaces as ns

# Функция для простых рекурсивных обходов
def go_recursive(root, func, args = []):
    points = root.xpath('./ncx:navPoint', namespaces = ns)
    if points:
        for point in points:
            n_args = func(point, args)
            n_args = go_recursive(point, func, n_args)
        return n_args
    return args

def rec_ls(point, args):
    tree = args[0]
    label = point.xpath('./ncx:navLabel/ncx:text', namespaces = ns)
    if label:
        if 'playOrder' in point.attrib.keys():
            branch = tree.add(f"{label[0].text} [magenta]{point.attrib['playOrder']}[/magenta]")
        else:
            branch = tree.add(f"{label[0].text} [magenta]{point.attrib['id']}[/magenta]")
        return [branch]

def rec_change_order(point, args):
    # args[0] = order
    # args[1] = src_in_toc
    
    args[0] += 1
    point.attrib['playOrder'] = str(args[0])
    contentL = point.xpath('./ncx:content/@src', namespaces = ns)
    if contentL:
        args[1].append(contentL[0])
    return args

def change_order(root):
    src_in_toc = []
    nav_points = root.xpath('//ncx:navMap/ncx:navPoint', namespaces = ns)
    if nav_points:
        order = 0
        for point in nav_points:
            order += 1
            point.attrib['playOrder'] = str(order)
            contentL = point.xpath('./ncx:content/@src', namespaces = ns)
            src_in_toc.append(contentL[0] if contentL else None)
            args = go_recursive(point, rec_change_order, [order, src_in_toc])
            order = args[0]
            src_in_toc = args[1]
        return order, src_in_toc
    return 0, None

def ls(root):
    doc_title = root.xpath('//ncx:docTitle/ncx:text', namespaces = ns)
    if doc_title:
        print("[blue]Doc Title:[/blue]", doc_title[0].text, '\n')
    
    nav_points = root.xpath('//ncx:navMap/ncx:navPoint', namespaces = ns)
    if nav_points:
        print("[cyan]Table of contents[/cyan]")
        print("--------------------")
        for point in nav_points:
            label = point.xpath('./ncx:navLabel/ncx:text', namespaces = ns)
            if label:
                if 'playOrder' in point.attrib.keys():
                    tree = Tree(f"{label[0].text} [magenta]{point.attrib['playOrder']}[/magenta]")
                else:
                    tree = Tree(f"{label[0].text} [magenta]{point.attrib['id']}[/magenta]")
                
                go_recursive(point, rec_ls, [tree])
            print(tree)

def show(el):
    labelL = el.xpath('./ncx:navLabel/ncx:text/text()', namespaces = ns)
    label = labelL[0] if labelL else None
    
    print("[blue]Label:", label)
    
    print("[cyan]id:", el.attrib['id'])
    if 'playOrder' in el.attrib.keys():
        print('[cyan]playOrder:', el.attrib['playOrder'])
    
    contentL = el.xpath('./ncx:content/@src', namespaces = ns)
    content = contentL[0] if contentL else None
    
    print("[yellow]Content:", content)

def to_any_case(el, action):
    labelL = el.xpath('./ncx:navLabel/ncx:text', namespaces = ns)
    label = labelL[0] if labelL else print(labelL)
    match action:
        case 'upper':
            label.text = label.text.upper()
        case 'lower':
            label.text = label.text.lower()
        case 'capitalize':
            text = label.text
            if '. ' in text:
                new_text = ''
                sentences = text.split('. ')
                for index, sent in enumerate(sentences):
                    new_text += sent.capitalize()
                    if sentences[-1] != sent:
                        new_text += '. '
                label.text = new_text
            else:
                label.text = label.text.capitalize()
        case 'title':
            label.text = label.text.title()

def iba_first_split(arg, inputs = True):
    if not inputs:
        arg = ' ' + arg
    
    if ' in ' in arg:
        input_orders, destination = arg.split(' in ')
        action = 'in'
    elif ' before ' in arg:
        input_orders, destination = arg.split(' before ')
        action = 'before'
    elif ' after ' in arg:
        input_orders, destination = arg.split(' after ')
        action = 'after'
    else:
        return
    
    if inputs:
        return input_orders, destination, action
    else:
        return destination, action

def second_arg_split(input_orders):
    if ' ' in input_orders:
        orders = input_orders.split()
    else:
        orders = [input_orders]
    return orders

def put(root, arg):
    input_orders, destination, action = iba_first_split(arg)
    
    if not action:
        print("Unknown option for 'put', try again.")
        return
    
    orders = second_arg_split(input_orders)
    
    dests = root.xpath(f'//ncx:navPoint[@playOrder="{destination}"]', namespaces = ns)
    if not dests:
        dests = root.xpath(f'//ncx:navPoint[@id="{destination}"]', namespaces = ns)
    
    if dests:
        dest = dests[0]
        for order in orders:
            elements = root.xpath(f'//ncx:navPoint[@playOrder="{order}"]', namespaces = ns)
            if not elements:
                elements = root.xpath(f'//ncx:navPoint[@id="{order}"]', namespaces = ns)
            
            if elements:
                el = elements[0]
                
                match action:
                    case 'in':
                        dest.append(el)
                    case 'before':
                        dest.addprevious(el)
                    case 'after':
                        dest.addnext(el)

def get_free_id_or_order(root, new_value, what):
    value = root.xpath(f'//ncx:navPoint[@{what}="{new_value}"]', namespaces = ns)
    counter = 1
    while value:
        new_value_mod = new_value + f'-{counter}'
        value = root.xpath(f'//ncx:navPoint[@{what}="{new_value_mod}"]', namespaces = ns)
        counter += 1
    
    return new_value if counter == 1 else new_value_mod

def create_el(root):
    point = etree.Element('{' + ns['ncx'] + '}navPoint')
    label = etree.SubElement(point, '{' + ns['ncx'] + '}navLabel')
    text = etree.SubElement(label, '{' + ns['ncx'] + '}text')
    content = etree.SubElement(point, '{' + ns['ncx'] + '}content')
    
    print('[blue]Label')
    text.text = input('> ', style = style)
    print('[blue]Content')
    content.attrib['src'] = input('> ', style = style)
    point.attrib['id'] = get_free_id_or_order(
        root, 
        'id' + str(random.randint(1, 1000000)), 
        'id'
    )
    point.attrib['playOrder'] = get_free_id_or_order(
        root, 
        str(random.randint(1, 1000000)), 
        'playOrder'
    )
    
    return point

def add(root, sec_arg):
    destination, action = iba_first_split(sec_arg, inputs = False)
    
    if not action:
        print("Unknown option for 'add', try again.")
        return
    
    dests = root.xpath(f'//ncx:navPoint[@playOrder="{destination}"]', namespaces = ns)
    if not dests:
        dests = root.xpath(f'//ncx:navPoint[@id="{destination}"]', namespaces = ns)
    
    if dests:
        dest = dests[0]
        point = create_el(root)
        
        match action:
            case 'in':
                dest.append(point)
            case 'before':
                dest.addprevious(point)
            case 'after':
                dest.addnext(point)

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
