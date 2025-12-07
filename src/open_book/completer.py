from prompt_toolkit.completion import Completer, Completion, NestedCompleter
from prompt_toolkit.document import Document

class OpenCompleter(Completer):
    def __init__(self, nested_dict, global_completer, global_dest_completer, book_completer, book_dest_completer, cmd_with_many_paths):
        self.nested_dict = nested_dict
        self.global_completer = global_completer
        self.global_dest_completer = global_dest_completer
        self.book_completer = book_completer
        self.book_dest_completer = book_dest_completer
        self.base_completer = NestedCompleter.from_nested_dict(nested_dict)
        self.cmd_with_many_paths = cmd_with_many_paths
    
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        words = text.split()
        
        if not words:
            for completion in self.base_completer.get_completions(document, complete_event):
                yield completion
            return
        
        first_word = words[0]
        current_word = words[-1]
        
        if first_word not in self.nested_dict:
            for completion in self.base_completer.get_completions(document, complete_event):
                yield completion
            return
        
        elif first_word == 'pretty':
            if text.endswith(' '):
                if len(words) >= 2:
                    return
                
                for compl_text in self.nested_dict[first_word]:
                    yield Completion(compl_text)
                
            else:
                for compl_text in self.nested_dict[first_word]:
                    if compl_text.startswith(current_word) and current_word != compl_text:
                        yield Completion(compl_text, start_position = -len(current_word))
            return
        
        elif first_word in self.nested_dict and self.nested_dict[first_word] is self.global_completer:
            len_first_word = len(first_word) + 1 # С пробелом
            yield from self.get_path_completions(self.global_completer, text, document, complete_event, len_first_word)
            return

        elif first_word in self.nested_dict and self.nested_dict[first_word] is self.global_dest_completer and (current_word != first_word or text.endswith(' ')):
            len_first_word = len(first_word) + 1 # С пробелом
            yield from self.get_path_completions(self.global_dest_completer, text, document, complete_event, len_first_word)
            return 

        elif first_word in self.nested_dict and self.nested_dict[first_word] is self.book_completer and first_word not in self.cmd_with_many_paths:
            len_first_word = len(first_word) + 1 # С пробелом
            yield from self.get_path_completions(self.book_completer, text, document, complete_event, len_first_word)
            return
        
        elif first_word in self.nested_dict and self.nested_dict[first_word] is self.book_dest_completer and (current_word != first_word or text.endswith(' ')):
            len_first_word = len(first_word) + 1 # С пробелом
            yield from self.get_path_completions(self.book_dest_completer, text, document, complete_event, len_first_word)
            return
        
        elif first_word in self.cmd_with_many_paths:
            paths = text[len(first_word) + 1:].split(' : ')
            current_path = paths[-1]
            
            # Чтоб правильно отображалось после главной комманды
            if not current_path and text.endswith(' '):
                len_start = len(text)
                yield from self.get_path_completions(self.book_completer, text, document, complete_event, len_start)
            
            elif current_path:
                len_current = len(text) - len(current_path)
                yield from self.get_path_completions(self.book_completer, text, document, complete_event, len_current)
            
            return
        
        elif first_word == 'add':
            if ':to' not in words:
                paths = text[len(first_word) + 1:].split(' : ')
                current_path = paths[-1]
                
                # Чтоб правильно отображалось после главной комманды
                if not current_path and text.endswith(' '):
                    len_start = len(text)
                    yield from self.get_path_completions(self.global_completer, text, document, complete_event, len_start)
                
                elif current_word.startswith(':') and ':to' not in words:
                    yield Completion(
                        ':to',
                        start_position = -len(current_word),
                    )
                
                # Основное дополнение для путей
                elif current_path:
                    len_current = len(text) - len(current_path)
                    yield from self.get_path_completions(self.global_completer, text, document, complete_event, len_current)
            
            # Путь назначения
            else:
                _to = text.split(' :to ')
                if len(_to) == 2:
                    before_to = _to[0]
                    # after_to = _to[1] Не особо она здесь нужна, но пусть будет
                    len_after_to = len(before_to) + 5 # С :to
                    yield from self.get_path_completions(self.book_dest_completer, text, document, complete_event, len_after_to)
            
            return
    
    def get_path_completions(self, completer, text, document, complete_event, len_):
        sub_text = text[len_:]
        sub_document = Document(sub_text, cursor_position=document.cursor_position - len_)
        
        for completion in completer.get_completions(sub_document, complete_event):
            yield Completion(
                completion.text,
                start_position= 0,
                display=completion.display,
                display_meta=completion.display_meta
            )
