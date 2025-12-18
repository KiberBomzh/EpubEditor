import copy
import os
from pathlib import Path
from rich import print
from rich.prompt import Confirm
from prompt_toolkit.completion import PathCompleter

from epubeditor.prompt_input import input


def get_order(books):
    books = copy.deepcopy(books)
    counter = 0
    books_dict = {}
    for book in books:
        counter += 1
        
        book_name = f'[dim]{book.parent.name}/[/][blue]{book.name}[/]'
        print(counter, book_name)
        books_dict[counter] = book
    
    if Confirm.ask("Change order?"):
        while True:
            nums_str = input("New order or command (put, rm)")
            if nums_str.startswith('put'):
                nums_and_dest = nums_str[3:].strip()
                if 'after' in nums_and_dest:
                    nums_str, dest_str = nums_and_dest.split(' after ')
                    where = 'after'
                elif 'before' in nums_and_dest:
                    nums_str, dest_str = nums_and_dest.split(' before ')
                    where = 'before'
                else:
                    print('[red]Not valid command![/]')
                    continue
                
                
                try:
                    nums = []
                    for num in nums_str.split():
                        nums.append(int(num))
                        if int(num) not in books_dict.keys():
                            raise ValueError
                    
                except ValueError:
                    print("[red]Not valid target nums![/]")
                    continue
                
                try:
                    dest = int(dest_str)
                    if dest not in books_dict.keys() or dest in nums:
                        raise ValueError
                except ValueError:
                    print("[red]Not valid the dest num![/]")
                    continue
                
                
                if where == 'after':
                    for num in reversed(nums):
                        target_index = books.index(books_dict[num])
                        book = books.pop(target_index)
                        dest_index = books.index(books_dict[dest])
                        books.insert(dest_index + 1, book)
                elif where == 'before':
                    for num in nums:
                        target_index = books.index(books_dict[num])
                        book = books.pop(target_index)
                        dest_index = books.index(books_dict[dest])
                        books.insert(dest_index, book)
            
            elif nums_str.startswith('rm'):
                nums_str = nums_str[2:].strip()
                try:
                    nums = []
                    for num in nums_str.split():
                        nums.append(int(num))
                        if int(num) not in books_dict.keys():
                            raise ValueError
                    
                except ValueError:
                    print("[red]Not valid nums![/]")
                    continue
                
                if any(nums.count(num) > 1 for num in nums):
                    print("[red]The numbers should not be repeated![red]")
                    continue
                
                for num in nums:
                    book_index = books.index(books_dict[num])
                    del books[book_index]
            
            else:
                try:
                    nums = []
                    for num in nums_str.split():
                        nums.append(int(num))
                    
                except ValueError:
                    print("[red]Not valid input![/]")
                    continue
                
                if (
                    len(nums) != len(books) or 
                    any(num > counter for num in nums) or
                    any(nums.count(num) > 1 for num in nums)
                ):
                    print("[red]Not valid input![/]")
                    continue
                
                
                books.clear()
                for num in nums:
                    books.append(books_dict[num])
            
            break
        
        print('New order:')
        books = get_order(books)
    
    return books

def get_new_book():
    completer = PathCompleter(
        expanduser=True,
        file_filter=lambda name: Path(name).is_dir() and Path(name).stem[0] != '.',
        min_input_len=0,
        get_paths=lambda: ['.'],
    )
    
    while True:
        new_book_str = input("Enter path for a merged book", completer = completer)
        if '~/' in new_book_str:
            new_book_path = Path(os.path.expanduser(new_book_str))
        else:
            new_book_path = Path(new_book_str)
        
        if new_book_path.is_dir():
            new_book = new_book_path / 'merged_book.epub'
        elif new_book_path.parent.exists():
            new_book = new_book_path
        else:
            print("[red]Not valid path[/]")
            continue
        
        return new_book