from lxml import html

def deleteElements(elements):
    for el in elements:
        parent = el.getparent()
        parent.remove(el)
    
def replaceElements(elements, new_value, query, where):
    match where:
        case 'attr':
            for el in elements:
                for key, value in el.attrib.items():
                    if query == value:
                        el.attrib[key] = new_value
        case 'paragraph':
            for el in elements:
                el.text = el.text.replace(query, new_value)

def printElements(elements, file, where):
    print('--------------')
    print(file)
    local_counter = 0
    for el in elements:
        local_counter += 1
        match where:
            case 'attr':
                print(f"\t{el.attrib.items()}")
            case 'paragraph':
                print(f"\n{el.text}\n")
    
    print(f"Total in file {file}: {local_counter}\n\n")
    return local_counter

def main(temp_path, query, action: str, new_value = '', where = 'paragraph'):
    file_formats = ['.xhtml', '.html', '.htm']
    total_counter = 0
    for file in temp_path.rglob('*'):
        if file.is_file() and file.suffix.lower() in file_formats:
            tree = html.parse(file)
            root = tree.getroot()
            
            match where:
                # Поиск в аттрибутах
                case 'attr':
                    s_res = root.xpath(f'//*[@*[contains(., "{query}")]]')
                # Поиск в параграфах
                case 'paragraph':
                    s_res = root.xpath(f'//p[contains(text(), "{query}")]')
                    if not s_res:
                        s_res = root.xpath(f'//div[contains(text(), "{query}")]')
            
            if s_res:
                match action:
                    case 'print':
                        total_counter += printElements(s_res, file.relative_to(temp_path), where)
                    case 'remove':
                        deleteElements(s_res)
                        tree.write(file, encoding='utf-8', xml_declaration = True, pretty_print = True)
                    case 'replace':
                        replaceElements(s_res, new_value, query, where)
                        tree.write(file, encoding='utf-8', xml_declaration = True, pretty_print = True)
    if action == 'print':
        print('--------------')
        print(f'Total in book: {total_counter}')

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
