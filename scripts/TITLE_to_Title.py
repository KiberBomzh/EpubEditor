from lxml import html

def main(temp_path, query):
    file_formats = ['.xhtml', '.html', '.htm']
    
    for file in temp_path.rglob('*'):
        if file.is_file() and file.suffix.lower() in file_formats:
            tree = html.parse(file)
            root = tree.getroot()
            
            titles = root.xpath(query)
            for t in titles:
                text = t.text
                if '. ' in text:
                    new_text = ''
                    sentences = text.split('. ')
                    for index, sent in enumerate(sentences):
                        new_text += sent.capitalize()
                        if sentences[-1] != sent:
                            new_text += '. '
                    t.text = new_text
                else:
                    t.text = text.capitalize()
            
            tree.write(file, encoding='utf-8', xml_declaration = True, pretty_print = True)