from rich.prompt import Prompt
from rich import print

from epubeditor.metadata_editor.get_metadata import getMetadataRaw, getMetadata
from epubeditor.namespaces import namespaces

def print_help(metaReadList):
    print("Available options:")
    for key in metaReadList:
        if '_' not in key:
            print(f"\t-{key.title()}, [green]'{key}'[/]")


# Функция для удаления хвостов
def removeRefines(el, metadata, root):
    el_id = el.get('id')
    if el_id is None:
        return
    
    Id = '#' + el_id
    refines = root.xpath(f'//opf:meta[@refines="{Id}"]', namespaces = namespaces)
    if len(refines) > 1:
        for ref in refines:
            metadata.remove(ref)
    elif len(refines) == 1:
        metadata.remove(refines[0])

def main(action, root):
    metadataRead = getMetadata(root)
    metaReadList = list(metadataRead.keys())
    match action:
        case "title":
            metadata = getMetadataRaw(root)
            title = metadata['title']
            if title:
                if len(title) > 1:
                    print("It seems, there's more than one title.")
                    print("What do you want to remove?")
                    count = 1
                    for t in title:
                        print(f'\t-{count}. {t.text}')
                        count += 1
                    print("\t-Remove all, just type 'all'")
                    act = Prompt.ask('[green]Choose')
                    if act == 'all':
                        for t in title:
                            if metadata['version'] == '3.0':
                                removeRefines(t, metadata['metadata'], root)
                            metadata['metadata'].remove(t)
                    elif act.isdigit():
                        if len(title) < int(act):
                            print("Too large number.")
                        else:
                            t = title[int(act) - 1]
                            if metadata['version'] == '3.0':
                                removeRefines(t, metadata['metadata'], root)
                            metadata['metadata'].remove(t)
                    else:
                        print('Unknown option.')
                else:
                    t = title[0]
                    if metadata['version'] == '3.0':
                        removeRefines(t, metadata['metadata'], root)
                    metadata['metadata'].remove(t)
            else:
                print("There's nothing to remove.")
        case "author":
            metadata = getMetadataRaw(root)
            if metadata['creators']:
                if 'authors' in metaReadList:
                   print('There is more than one author, try "authors"') 
                else:
                    a = metadata['creators'][0]
                    if metadata['version'] == '3.0':
                        removeRefines(a, metadata['metadata'], root)
                    metadata['metadata'].remove(a)
            else:
                print("There's nothing to remove.")
        case "authors":
            metadata = getMetadataRaw(root)
            if metadata['creators']:
                if 'authors' in metaReadList:
                    print("Which author you want to remove?")
                    authors = metadata['creators']
                    count = 1
                    for author in authors:
                        print(f'\t-{count}. {author.text}')
                        count += 1
                    print("\t-Remove all, just type 'all'")
                    act = Prompt.ask("[green]Choose")
                    if act == 'all':
                        for a in authors:
                            if metadata['version'] == '3.0':
                                removeRefines(a, metadata['metadata'], root)
                            metadata['metadata'].remove(a)
                    elif act.isdigit():
                        if len(authors) < int(act):
                            print("Too large number.")
                        else:
                            a = authors[int(act) - 1]
                            if metadata['version'] == '3.0':
                                removeRefines(a, metadata['metadata'], root)
                            metadata['metadata'].remove(a)
                    else:
                        print('Unknown option.')
                else:
                    print('There is only one author, try "author"') 
            else:
                print("There's nothing to remove.")
        case "series":
            metadata = getMetadataRaw(root)
            if metadata['version'] == '2.0':
                series = metadata['series']
                series_index = metadata['series_index']
                if series:
                    if len(series) > 1:
                        print("It seems, there's more than one series.")
                        print("What do you want to remove?")
                        count = 1
                        for s in series:
                            print(f'\t-{count}. {s.get('content')}')
                            count += 1
                        print("\t-Remove all, just type 'all'")
                        act = Prompt.ask('[green]Choose')
                        if act == 'all':
                            for s in series:
                                metadata['metadata'].remove(s)
                            if series_index:
                                for s in series_index:
                                    metadata['metadata'].remove(s)
                        elif act.isdigit():
                            if len(series) < int(act):
                                print("Too large number.")
                            else:
                                metadata['metadata'].remove(series[int(act) - 1])
                                if series_index:
                                    if series_index[int(act) - 1]:
                                        metadata['metadata'].remove(series_index[int(act) - 1])
                        else:
                            print('Unknown option.')
                    else:
                        metadata['metadata'].remove(series[0])
                        if series_index:
                            metadata['metadata'].remove(series_index[0])
                else:
                    print("There's nothing to remove.")
            elif metadata['version'] == '3.0':
                collection = metadata['series']
                position = metadata['series_index']
                collection_type = root.xpath('//opf:meta[@property="collection-type"]', namespaces = namespaces)
                if collection:
                    if len(collection) > 1:
                        print("It seems, there's more than one collection.")
                        print("What do you want to remove?")
                        count = 1
                        for c in collection:
                            print(f'\t-{count}. {c.text}')
                            count += 1
                        print("\t-Remove all, just type 'all'")
                        act = Prompt.ask('[green]Choose')
                        if act == 'all':
                            for c in collection:
                                metadata['metadata'].remove(c)
                            if position:
                                for p in position:
                                    metadata['metadata'].remove(p)
                            if collection_type:
                                for c in collection_type:
                                    metadata['metadata'].remove(c)
                        elif act.isdigit():
                            if len(collection) < int(act):
                                print("Too large number.")
                            else:
                                metadata['metadata'].remove(collection[int(act) - 1])
                                if position:
                                    if position[int(act) - 1]:
                                        metadata['metadata'].remove(position[int(act) - 1])
                                if collection_type:
                                    if collection_type[int(act) - 1]:
                                        metadata['metadata'].remove(collection_type[int(act) - 1])
                        else:
                            print('Unknown option.')
                    else:
                        metadata['metadata'].remove(collection[0])
                        if position:
                            metadata['metadata'].remove(position[0])
                        if collection_type:
                            metadata['metadata'].remove(collection_type[0])
                else:
                    print("There's nothing to remove.")
        case "language":
            metadata = getMetadataRaw(root)
            language = metadata['language']
            if language:
                if len(language) > 1:
                    print("It seems, there's more than one language.")
                    print("What do you want to remove?")
                    count = 1
                    for lan in language:
                        print(f'\t-{count}. {lan.text}')
                        count += 1
                    print("\t-Remove all, just type 'all'")
                    act = Prompt.ask('[green]Choose')
                    if act == 'all':
                        for lan in language:
                            metadata['metadata'].remove(lan)
                    elif act.isdigit():
                        if len(language) < int(act):
                            print("Too large number.")
                        else:
                            metadata['metadata'].remove(language[int(act) - 1])
                    else:
                        print('Unknown option.')
                else:
                    metadata['metadata'].remove(language[0])
            else:
                print("There's nothing to remove.")
        case "help":
            print_help(metaReadList)
        case _:
            print("Unknown option for rm, try 'rm help'")

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
