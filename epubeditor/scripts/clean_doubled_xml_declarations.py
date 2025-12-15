def rm_from_text(text, query):
    query = query.lower()
    while query in text:
        start = text.lower().find(query)
        end = start + len(query)
        if text[end] == '\n':
            end += 1
        
        text = text[:start] + text[end:]
    return text

def remove_declaration(text):
    xml_decl1 = "<!--?xml version='1.0' encoding='UTF-8'?-->"
    xml_decl2 = '<!--?xml version="1.0" encoding="UTF-8"?-->'
    
    if xml_decl1 in text or xml_decl2 in text:
        text = rm_from_text(text, xml_decl1)
        text = rm_from_text(text, xml_decl2)
    
    return text

def main(temp_path):
    html_formats = ['.xhtml', '.html', 'htm']
    for file in temp_path.rglob('*'):
        if file.suffix.lower() in html_formats:
            file_content = file.read_text()
            file.write_text(remove_declaration(file_content))