from prompt_toolkit.completion import Completer, Completion, NestedCompleter

class TocCompleter(Completer):
    def __init__(self, nested_dict, order_list, iba, exceptions, complex_commands):
        self.nested_dict = nested_dict
        self.order_list = order_list
        self.exceptions = exceptions
        self.iba = iba
        self.complex_commands = complex_commands
        self.base_completer = NestedCompleter.from_nested_dict(nested_dict)
    
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
        
        # Вариант когда нужно ввести только один вариант с order_list
        if first_word in self.exceptions:
            if text.endswith(' '):
                if len(words) >= 2:
                    return
                
                for order in self.order_list.keys():
                    yield Completion(order)
            else:
                for order in self.order_list.keys():
                    if order.startswith(current_word) and current_word != order:
                        yield Completion(order, start_position = -len(current_word))
            return
        
        if first_word in self.nested_dict and first_word not in self.complex_commands and self.nested_dict[first_word] is not None:
            for order in self.order_list.keys():
                if text.endswith(' '):
                    if order not in words:
                        yield Completion(order)
                elif order.startswith(current_word) and current_word != order and order not in words:
                    yield Completion(order, start_position = -len(current_word))
            return
        
        # Обработка сложных комманд
        if first_word == 'put':
            # Первые значения для put (одно или несколько)
            if not any(act in words for act in self.iba):
                # Если на конце пробел то проверять только чтоб не предлагались слова которые уже есть
                if text.endswith(' '):
                    for order in self.order_list.keys():
                        if order not in words:
                            yield Completion(order)
                
                # Иначе проверять ещё и текущее слово чтоб его можно было дополнить
                else:
                    for order in self.order_list.keys():
                        if order.startswith(current_word) and current_word != order and order not in words:
                            yield Completion(order, start_position = -len(current_word))
                    
            
            # Вторая комманда (in, before, after)
            if any(current_word in act for act in self.iba) and not any(act in words for act in self.iba):
                for act in self.iba.keys():
                    if act.startswith(current_word):
                        yield Completion(act, start_position = -len(current_word))
                
            
            # Концовка, куда добавлять
            if len(words) >= 2:
                if any(words[-2] in act for act in self.iba) or any(current_word in act for act in self.iba):
                    for order in self.order_list.keys():
                        if text.endswith(' ') and any(current_word in act for act in self.iba):
                            if order not in words:
                                yield Completion(order)
                        else:
                            if order.startswith(current_word) and current_word != order and order not in words:
                                yield Completion(order, start_position = -len(current_word))
            return
        
        elif first_word == 'add':
            # Подсказка in/before/after
            if not any(act in words for act in self.iba):
                if text.endswith(' '):
                    for act in self.iba.keys():
                        yield Completion(act)
                elif any(current_word in act for act in self.iba):
                    for act in self.iba.keys():
                        if act.startswith(current_word):
                            yield Completion(act, start_position = -len(current_word))
            else:
                if text.endswith(' '):
                    if any(w in self.order_list for w in words):
                        return
                
                    for order in self.order_list.keys():
                        yield Completion(order)
                else:
                    for order in self.order_list.keys():
                        if order.startswith(current_word) and current_word != order:
                            yield Completion(order, start_position = -len(current_word))
            return