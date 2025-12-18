def rm_from_text(text):
    start_txt = '<!--?'
    end_txt = '?-->'
    while start_txt in text and end_txt in text:
        start = text.find(start_txt)
        end = text.find(end_txt) + len(end_txt)
        if text[end] == '\n':
            end += 1
        
        text = text[:start] + text[end:]
    return text

def remove_declaration(text):
    xml_decl1 = "<!--?xml version='1.0' encoding='UTF-8'?-->"
    xml_decl2 = '<!--?xml version="1.0" encoding="UTF-8"?-->'
    
    if xml_decl1 in text or xml_decl2 in text:
        text = rm_from_text(text)
    
    return text

def main(temp_path):
    html_formats = ['.xhtml', '.html', 'htm']
    for file in temp_path.rglob('*'):
        if file.suffix.lower() in html_formats:
            file_content = file.read_text()
            file.write_text(remove_declaration(file_content))