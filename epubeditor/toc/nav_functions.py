from rich.tree import Tree
from rich import print
from lxml import html

from epubeditor.toc.functions import second_arg_split, iba_first_split
from epubeditor.prompt_input import input

def get_nav(root):
    nav = root.xpath('//nav[@id="toc"]')
    if nav:
        nav = nav[0]
    else:
        raise TypeError('Nav not found!')
    return nav

def go_recursive(root, func, args = []):
    points = root.xpath('./ol/li')
    if points:
        for point in points:
            n_args = func(point, args)
            n_args = go_recursive(point, func, n_args)
        return n_args
    return args

def rec_ls(point, args):
    tree = args[0]
    global points_order
    label = point.find('a')
    if label is not None:
        branch = tree.add(f'{label.text} [magenta]{points_order[point]}[/]')
        return [branch]

# Ключ - элемент, значение - order
points_order = {}
# Ключ - order, значение - элемент
points_order_rev = {}
# Пурга какая-то выходит,
# придумать потом что-то более внятное

order = 0

def rec_init_order(point, args):
    global points_order
    global order
    
    order += 1
    points_order[point] = str(order)

def init_order(root):
    global points_order
    global points_order_rev
    global order
    order = 0
    
    nav = get_nav(root)
    
    go_recursive(nav, rec_init_order)
    
    for key, value in points_order.items():
        points_order_rev[value] = key

def ls(root):
    nav = get_nav(root)
    
    nav_points = nav.xpath('./ol/li')
    if nav_points:
        global points_order
        for point in nav_points:
            label = point.find('a')
            if label is not None:
                tree = Tree(f'{label.text} [magenta]{points_order[point]}[/]')
                
                go_recursive(point, rec_ls, [tree])
            print(tree)

def show(root, sec_arg):
    global points_order_rev
    try:
        element = points_order_rev[sec_arg]
    except KeyError:
        print(f"Wrong num: {sec_arg}, try again.")
        return
    
    a = element.find('a')
    label = a.text
    
    print("[blue]Label:", label)
    
    href = a.get('href')
    print("[yellow]Content:", href)

def edit(root, sec_arg):
    global points_order_rev
    
    try:
        el = points_order_rev[sec_arg]
    except KeyError:
        print(f"Wrong num: {sec_arg}, try again.")
        return
    
    a = el.find('a')
    a.text = input('Label', default = a.text)
    
    a.attrib['href'] = input('Content', default = a.get('href'))

def rm(root, sec_arg):
    orders = second_arg_split(sec_arg)
    global points_order_rev
    global points_order
    
    for order in orders:
        try:
            element = points_order_rev[order]
            del points_order[element]
            del points_order_rev[order]
            element.getparent().remove(element)
        except KeyError:
            print(f"Wrong num: {order}.")

def to_any_case(root, action, sec_arg):
    global points_order
    
    if sec_arg is not None:
        orders = second_arg_split(sec_arg, get_orders(root))
        if orders is None:
            return
        
        for order in orders:
            try:
                el = points_order_rev[order]
                to_any_case_do(el, action)
            except KeyError:
                print(f"Wrong num: {order}.")
    else:
        for el in points_order:
            to_any_case_do(el, action)

def to_any_case_do(el, action):
    a = el.find('a')
    if a is None:
        return
    
    match action:
        case 'upper':
            a.text = a.text.upper()
        case 'lower':
            a.text = a.text.lower()
        case 'capitalize':
            text = a.text
            if '. ' in text:
                new_text = ''
                sentences = text.split('. ')
                for index, sent in enumerate(sentences):
                    new_text += sent.capitalize()
                    if sentences[-1] != sent:
                        new_text += '. '
                a.text = new_text
            else:
                a.text = a.text.capitalize()
        case 'title':
            a.text = a.text.title()

def add(root, sec_arg):
    global points_order_rev
    destination, action = iba_first_split(sec_arg, inputs = False)
    
    if not action:
        print("Unknown option for 'add', try again.")
        return
    
    try:
        dest = points_order_rev[destination]
    except KeyError:
        print(f"Wrong destination num: {destination}, try again.")
        return
    
    li = html.Element('li')
    a = html.Element('a')
    li.append(a)
    
    a.text = input('Label')
    a.attrib['href'] = input('Content')
    
    match action:
        case 'in':
            ol = dest.find('ol')
            if ol is None:
                ol = html.Element('ol')
                dest.append(ol)
            
            ol.append(li)
        case 'before':
            dest.addprevious(li)
        case 'after':
            dest.addnext(li)
    
    init_order(root)

def put(root, arg):
    global points_order_rev
    input_orders, destination, action = iba_first_split(arg)
    
    if not action:
        print("Unknown option for 'put', try again.")
        return
    
    orders = second_arg_split(input_orders, get_orders(root))
    if orders is None:
        return
    
    try:
        dest = points_order_rev[destination]
    except KeyError:
        print(f"Wrong destination num: {destination}, try again.")
        return
    
    if action == 'after':
        orders = reversed(orders)
    
    for order in orders:
        try:
            li = points_order_rev[order]
                
            match action:
                case 'in':
                    ol = dest.find('ol')
                    if ol is None:
                        ol = html.Element('ol')
                        dest.append(ol)
                
                    ol.append(li)
                case 'before':
                    dest.addprevious(li)
                case 'after':
                    dest.addnext(li)
        except KeyError:
            print(f"Wrong num: {order}.")

def rec_get_orders(point, args):
    global points_order
    order_list = args[0]
    order = points_order[point]
    order_list[order] = None
    return [order_list]

# Возвращает все номера элементов
# для комплитера, аргумент нужен
# для правильного вызова
def get_orders(root):
    nav = get_nav(root)
    order_list = {}
    go_recursive(nav, rec_get_orders, [order_list])
    return order_list

# Заглушка, которая просто возвращает
# количество елементов и
# список со всеми ссылками на файлы
# Аргумент нужен для совместимости
def change_order(root):
    global points_order_rev
    
    src_in_toc = []
    order = 0
    len_points = len(points_order_rev)
    while len_points > order:
        order += 1
        try:
            li = points_order_rev[str(order)]
        except KeyError:
            continue
        
        a = li.find('a')
        src_in_toc.append(a.get('href'))
    
    return order, src_in_toc

if __name__ == "__main__":
    print("This is just module, try to run cli.py")