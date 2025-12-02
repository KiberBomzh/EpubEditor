from lxml import etree, html

from src.console_prompt import main as prompt
from src.toc import sort_spine
from src.toc.completer import TocCompleter

def optionHandl(action, args):
    root = args[0]
    what_is_it = args[1]
    if what_is_it == 'toc':
        from src.toc.functions import ls, add, show, to_any_case, put, edit, rm
    elif what_is_it == 'nav':
        from src.toc.nav_functions import ls, add, show, to_any_case, put, edit, rm
    
    if len(args) > 2:
        sec_arg = args[2].strip()
    else:
        sec_arg = None
    
    match action:
        case 'ls':
            ls(root)
        case 'show':
            if sec_arg is not None:
                show(root, sec_arg)
            else:
                print('Option needs second argument, try again.')
        case 'edit':
            if sec_arg is not None:
                edit(root, sec_arg)
            else:
                print('Option needs second argument, try again.')
        case 'put':
            if sec_arg is not None:
                put(root, sec_arg)
            else:
                print('Option needs second argument, try again.')
        case 'rm':
            if sec_arg is not None:
                rm(root, sec_arg)
            else:
                print('Option needs second argument, try again.')
        case 'add':
            if sec_arg is not None:
                add(root, sec_arg)
            else:
                print('Option needs second argument, try again.')
        case 'upper' | 'lower' | 'capitalize' | 'title':
           to_any_case(root, action, sec_arg) 
        case _:
            print("Unknown option, try again.")

def main(toc, opf, what_is_it, path = 'epubeditor/toc'):
    if what_is_it == 'toc':
        from src.toc.functions import change_order, get_orders
        toc_tree = etree.parse(toc)
        toc_root = toc_tree.getroot()
    elif what_is_it == 'nav':
        from src.toc.nav_functions import change_order, get_orders, init_order
        toc_tree = html.parse(toc)
        toc_root = toc_tree.getroot()
        init_order(toc_root)

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
    
    order_list = get_orders(toc_root)
    
    iba = {
        'in': order_list,
        'before': order_list,
        'after': order_list,
    }
    
    completer = TocCompleter({
        'ls': None,
        'show': order_list,
        'edit': order_list,
        'add': iba,
        'put': iba,
        'rm': order_list,
        'upper': order_list,
        'lower': order_list,
        'capitalize': order_list,
        'title': order_list,
        '..': None,
        'exit': None,
        'help': None,
    }, order_list, iba, ['show', 'edit'], ['put', 'add'])
    
    act = prompt(optionHandl, completer, help_msg, path = path, args = [toc_root, what_is_it])
    
    order, src_in_toc_raw = change_order(toc_root)
    if order > 0:
        src_in_toc = sort_spine.raw_to_src(src_in_toc_raw, toc.parent, opf.parent)
        sort_spine.main(opf_root, src_in_toc)
    
    if what_is_it == 'toc':
        toc_tree.write(toc, encoding = 'utf-8', xml_declaration = True, pretty_print = True)
    elif what_is_it == 'nav':
        toc_tree.write(toc, encoding = 'utf-8', pretty_print = True)
    
    opf_tree.write(opf, encoding = 'utf-8', xml_declaration = True, pretty_print = True)
    return act

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
