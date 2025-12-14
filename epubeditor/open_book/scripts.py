from epubeditor.scripts.toc_from_titles import main as toc_from_titles


scripts_list = [
    'toc_from_titles'
]

def main(temp_path, arg):
    if isinstance(arg, list):
        args = arg
        action = args[0]
    else:
        args = arg.split()
        action = args[0]
        if action not in scripts_list:
            print("There's no such script:", action)
            return
    
    match action:
        case 'toc_from_titles':
            toc_from_titles(temp_path)
