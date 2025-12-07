from lxml import html

new_file_content: str

def get_text(text_raw):
    class Element():
        def __init__(self, element):
            self.element = element
    
    text = text_raw.strip()
    # Удаление левого элемента
    start = text.find('<')
    end = text.find('>') + 1
    text = text[:start] + text[end:]
    
    # Удаление правого элемента
    start = text.rfind('<')
    text = text[:start]
    
    # Убрать переносы строк
    if '\n' in text:
        text_list = text.splitlines()
        text = ''
        for line in text_list:
            line = line.strip()
            text += line
    
    # Если внутри есть элементы то нужно их вручную проверить
    # Метод .tostring() не правильно обрабатывает элементы типа <br/>, <img/>, <p/>
    if '<' in text or '>' in text:
        elements = []
        txt = text
        while txt and ('<' in txt or '>' in txt):
            index = txt.find('<')
            txt = txt[index:]
            element = ''
            for char in txt:
                if char != '>':
                    element += char
                else:
                    element += char
                    break
            element = element.strip()
            if element:
                el = Element(element)
                elements.append(el)
            index = txt.find('>') + 1
            txt = txt[index:]
    
    # Поиск пар элементов
    start_elements = []
    end_elements = []
    for element in elements:
        el = element.element
        start = el.find('<')
        if el[start + 1] == '/':
            end_elements.append(element)
        else:
            start_elements.append(element)
    
    for element in start_elements:
        el = element.element
        start = el.find('<') + 1
        end = el.find(' ')
        if end == -1:
            end = el.find('>')
        tag = el[start:end]
        if '/' in tag:
            index = tag.find('/')
            if tag[index] == tag[-1]:
                tag = tag[:index]
        
        element.tag = tag
        
        end = el.find('>')
        body = el[start:end]
        if '/' in body:
            index = body.find('/')
            if body[index] == body[-1]:
                body = body[:index]
        
        element.body = body
    
    for element in end_elements:
        el = element.element
        start = el.find('/') + 1
        end = el.find('>')
        body = el[start:end]
        element.body = body
        
        if ' ' not in body:
            tag = body
        else:
            index = body.find(' ')
            tag = body[:index]
        element.tag = tag
    
    sole_elements = []
    for element in start_elements:
        el = element.element
        tag = element.tag
        is_tag_found = False
        for index, end_element in enumerate(end_elements):
            end_tag = end_element.tag
            if tag == end_tag:
                is_tag_found = True
                del end_elements[index]
                break
        
        if not is_tag_found:
            sole_elements.append(element)
    
    for element in sole_elements:
        el = element.element
        if '/' not in el:
            index = text.find(el)
            els_end = text[index:].find('>') + index
            text = text[:els_end] + '/' + text[els_end:]
    
    
    # while '<' in text and '>' in text:
    #     start = text.find('<')
    #     end = text.find('>') + 1
    #     text = text[:start] + text[end:]
    return text.strip()

def rec_walk(root, tab = 0, was_text = False, line_indent = False):
    global new_file_content
    children = root.getchildren()
    style_tags = ['strong', 'b', 'i', 'em', 'small', 'u', 'br']
    
    # Обработка атрибутов элемента
    attributes = []
    for key, value in root.attrib.items():
        attr = f'{key}="{value}"'
        attributes.append(attr)
    
    # Строка внутри < > кавычек
    tag = root.tag
    attrs = ' '.join(attributes)
    element_inside = f"{tag} {attrs}" if attrs else f"{tag}"
    
    # Текст внутри элемента, для правильной работы if-else
    text = root.text.strip() if root.text else ""
    # Текст может быть так размещён что через .text
    # его получить нельзя, в этом случае проходимся вручную
    # if not text and tag not in ['html', 'body', 'head']:
    #     text_raw = html.tostring(root, encoding = 'unicode')
    #     text = get_text(text_raw)
    
    # Если нет дочерних элементов и текста
    # Выводить только один элемент
    # Без закрывающего тега
    if not text and not children:
        element_str = f"<{element_inside}/>"
        if not was_text:
            element_str += '\n'
    else:
        element_str = f"<{element_inside}>"
    
    # Если не было текста в родительском заходе
    # И текущий тег не в стилях
    # Добавить таб
    start_el = (
        ('\t' * (tab if not was_text and tag not in style_tags else 0)) + 
        element_str
    )
    
    # Какой либо элемент из дочерних есть в стилях
    is_child_tag_in_styles = any(child.tag in style_tags for child in children)
    
    # Если есть дочерние элементы, нету текста
    # И не текущий не какой-то из дочерних элементов
    # Не находится в стилях
    # Добавить перенос на новую строку
    if children and not text and not was_text:
        if not is_child_tag_in_styles and tag not in style_tags:
            start_el += '\n'
    
    # Запись в переменную с будущим содержимым файла
    new_file_content += start_el
    
    # Если есть текст добавить и его
    if text:
        new_file_content += text
    
    if not text and is_child_tag_in_styles:
        text_raw = html.tostring(root, encoding = 'unicode')
        text = get_text(text_raw)
        new_file_content += text
    else:
        # Увеличение количества табо отступа
        # И рекурсивных проходка по всем дочерним элементам
        tab += 1
        for child in children:
            rec_walk(child, tab, bool(text))
            
            if child != children[-1] and line_indent:
                new_file_content += '\n'
    
    # Если есть или текст или дочерние элементы
    # Выводить закрывающий тег
    if text or children:
        end_el = (
            '\t' * (tab - 1 if children and not was_text and not text and tag not in style_tags and not is_child_tag_in_styles else 0) +
            f"</{tag}>" +
            ('\n' if not was_text and tag not in style_tags else '')
        )
        new_file_content += end_el

def main(file, line_indent = False, xml_declaration = False):
    global new_file_content
    if xml_declaration:
        new_file_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    else:
        new_file_content = ''
    
    root = html.parse(file).getroot()
    rec_walk(root, line_indent = line_indent)
        
    file.write_text(new_file_content)

if __name__ == "__main__":
    print("This is just module, try to run cli.py")