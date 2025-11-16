from rich.prompt import Prompt

from src.metadata_editor.get_metadata import getMetadataRaw
from src.metadata_editor import create_sort

from src.console_prompt import main as prompt

def optionHandl(action, args):
    root = args[0]
    match action:
        case "title":
            metadata = getMetadataRaw(root)
            new_title = Prompt.ask("[green]New title")
            if new_title:
                metadata.get('title')[0].text = new_title
        case "author":
            metadata = getMetadataRaw(root)
            if len(metadata['creators']) > 1:
               print('There is more than one author, try "authors"') 
            else:
                new_author = Prompt.ask("[green]New  author")
                if new_author:
                    metadata.get('creators')[0].text = new_author
        case "authors":
            metadata = getMetadataRaw(root)
            if len(metadata['creators']) > 1:
                for creator in metadata['creators']:
                    print(f"Old author: {creator.text}")
                    new_author = Prompt.ask("[green]New author")
                    if new_author:
                        creator.text = new_author
            else:
                print('There is only one author, try "author"') 
        case "language":
            metadata = getMetadataRaw(root)
            new_language = Prompt.ask("[green]New language")
            if new_language:
                metadata.get('language')[0].text = new_language
        case "series":
            metadata = getMetadataRaw(root)
            if metadata['series'] and metadata['series_index']:
                if metadata['version'] == '2.0':
                    new_series = Prompt.ask("[green]New series")
                    new_series_index = Prompt.ask("[green]New series index")
                    if new_series:
                        metadata.get('series')[0].set('content', new_series)
                    if new_series_index:
                        metadata.get('series_index')[0].set('content', new_series_index)
                elif metadata['version'] == '3.0':
                    new_series = Prompt.ask("[green]New series")
                    new_series_index = Prompt.ask("[green]New series index")
                    if new_series:
                        metadata.get('series')[0].text = new_series
                    if new_series_index:
                        metadata.get('series_index')[0].text = new_series_index
            else:
                print("There's no series, try add.")
        case "sort":
            create_sort.createSort(root)
            print('Added.')
        case _:
            print("Unknown option, try again.")

def main(root, metadataRead, path):
    metaReadList = list(metadataRead.keys())
    optList = []
    for key in metaReadList:
        if '_' not in key:
            optList.append(key)
    
    help_msg = "Available options:"
    for opt in optList:
        help_msg += f"\n\t-{opt.title()}, [green]'{opt}'[/]"
    help_msg += "\n\t-Create author's sort name, print [green]'sort'[/]" + "\n\t-Go back, [green]'..'[/]" + "\n\t-Exit"
    optList.append('sort')
    optList.append('..')
    
    return prompt(optionHandl, optList, help_msg, path = path + '/set', args = [root])

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
