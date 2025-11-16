from lxml import etree
from rich.prompt import Prompt
from rich import print

from src.console_prompt import main as prompt
from src.toc.functions import ls, add, show, to_any_case, put, second_arg_split, create_el, change_order
from src.toc.sort_spine import main as sort_spine

ns = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}

def optionHandl(action, args):
    root = args[0]
    if len(args) > 1:
        sec_arg = args[1]
    else:
        sec_arg = None
    
    match action:
        case 'ls':
            ls(root)
        case 'show':
            if sec_arg:
                elements = root.xpath(f'//ncx:navPoint[@playOrder="{sec_arg}"]', namespaces = ns)
                if elements:
                    el = elements[0]
                    show(el)
                else:
                    elements = root.xpath(f'//ncx:navPoint[@id="{sec_arg}"]', namespaces = ns)
                    if elements:
                        el = elements[0]
                        show(el)
            else:
                print('Option needs second argument, try again.')
        case 'edit':
            if sec_arg:
                elements = root.xpath(f'//ncx:navPoint[@playOrder="{sec_arg}"]', namespaces = ns)
                if not elements:
                    elements = root.xpath(f'//ncx:navPoint[@id="{sec_arg}"]', namespaces = ns)
                
                if elements:
                    el = elements[0]
                    labelL = el.xpath('./ncx:navLabel/ncx:text', namespaces = ns)
                    label = labelL[0] if labelL else print(labelL)
                    print('[blue]Old label:[/blue]', label.text)
                    new_label = Prompt.ask('[green]New label')
                    if new_label:
                        label.text = new_label
            else:
                print('Option needs second argument, try again.')
        case 'put':
            if sec_arg:
                put(root, sec_arg)
            else:
                print('Option needs second argument, try again.')
        case 'rm':
            if sec_arg:
                orders = second_arg_split(sec_arg)
                
                for order in orders:
                    elements = root.xpath(f'//ncx:navPoint[@playOrder="{order}"]', namespaces = ns)
                    if elements:
                        elements[0].getparent().remove(elements[0])
                    else:
                        elements = root.xpath(f'//ncx:navPoint[@id="{order}"]', namespaces = ns)
                        if elements:
                            elements[0].getparent().remove(elements[0])
            else:
                nav_map = root.find('ncx:navMap', namespaces = ns)
                elements = nav_map.xpath('./ncx:navPoint', namespaces = ns)
                for el in elements:
                    nav_map.remove(el)
        case 'add':
            if sec_arg:
                add(root, sec_arg)
            else:
                nav_map = root.xpath('//ncx:navMap', namespaces = ns)
                point = create_el(root)
                if nav_map:
                    nav_map[0].append(point)
        case 'upper' | 'lower' | 'capitalize' | 'title':
            if sec_arg:
                orders = second_arg_split(sec_arg)
                
                for order in orders:
                    elements = root.xpath(f'//ncx:navPoint[@playOrder="{order}"]', namespaces = ns)
                    if elements:
                        to_any_case(elements[0], action)
                    else:
                        elements = root.xpath(f'//ncx:navPoint[@id="{order}"]', namespaces = ns)
                        if elements:
                            to_any_case(elements[0], action)
                    
            else:
                elements = root.xpath('//ncx:navPoint', namespaces = ns)
                for el in elements:
                    to_any_case(el, action)
        case _:
            print("Unknown option, try again.")

def main(toc, opf, path = 'epubeditor/toc'):
    toc_tree = etree.parse(toc)
    toc_root = toc_tree.getroot()
    opf_tree = etree.parse(opf)
    opf_root = opf_tree.getroot()
    help_msg = ("Available options:\n" +
            "\t-Show all elements                   [green]'ls'[/]\n" + 
            "\t-Show element                        [green]'show'[/] [magenta]num[/]\n" + 
            "\t-Edit element's label                [green]'edit'[/] [magenta]num[/]\n" + 
            "\t-Move elements                       [green]'put'[/] [magenta]num1 num2 .. numN[/] [dark_orange]{in/before/after}[/] [magenta]num[/]\n" + 
            "\t-Delete element                      [green]'rm'[/] [magenta]num1 num2 .. numN[/]\n" + 
            "\t-Add element                         [green]'add'[/] [dark_orange]{in/before/after}[/] [magenta]num[/]\n" + 
            "\t-Change case for [magenta]num[/] or for all      [green]'{upper/lower/capitalize/title}'[/] [magenta]num1 num2 .. numN[/]\n" +
            "\t-Go back                             [green]'..'[/]\n" +
            "\t-Exit")
    optList = ['ls', 'show', 'edit', 'put', 'rm', 'add', 'upper', 'lower', 'capitalize', 'title', '..']
    act = prompt(optionHandl, optList, help_msg, path = path, args = [toc_root])
    
    order, src_in_toc = change_order(toc_root)
    if order > 0:
        sort_spine(opf_root, src_in_toc)
    
    toc_tree.write(toc, encoding='utf-8', xml_declaration = True, pretty_print = True)
    opf_tree.write(opf, encoding='utf-8', xml_declaration = True, pretty_print = True)
    return act

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
