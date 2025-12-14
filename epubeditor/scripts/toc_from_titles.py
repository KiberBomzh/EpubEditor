from lxml import etree, html
from epubeditor.open_book.functions import get_files_in_spine_order
from epubeditor.open_book.files_operations import get_rel
from epubeditor.namespaces import namespaces as ns


# Флаги настройки
include_subtitles = False
all_h = False


def get_toc(temp_path):
    from epubeditor.editor.main import getOpf, getToc
    
    container = temp_path / 'META-INF/container.xml'
    opf = temp_path / getOpf(container)
    toc_tuple_str, what_is_it = getToc(opf)
    toc = (opf.parent / toc_tuple_str[0]).resolve()
    
    if what_is_it == 'toc and nav':
        nav = (opf.parent / toc_tuple_str[1]).resolve()
        toc_tuple = (toc, nav)
    else:
        toc_tuple = (toc,)
    
    return toc_tuple, what_is_it

def get_text(text_raw):
    text = text_raw.strip()
    while '<' in text and '>' in text:
        start = text.find('<')
        end = text.find('>') + 1
        text = text[:start] + text[end:]
    
    lines = text.splitlines()
    text = ''
    for line in lines:
        if line != lines[-1]:
            text += line.strip() + ' '
        else:
            text += line.strip()
    
    return text.strip()

def get_label(element):
    label = element.text
    if label is not None:
        label = label.strip()
    
    if label is None or label == '':
        label = ''
        for child in element.getchildren():
            child_label = child.text
            if child_label is not None:
                child_label = child_label.strip()
            
            if child_label is not None and child_label != '':
                label += ' ' + child_label
    
    if label == '':
        text_raw = html.tostring(element, encoding = 'unicode')
        label = get_text(text_raw)
    
    return label.strip()


class Title():
    def __init__(self, element, file_rel_to_toc, toc_order):
        self.element = element
        
        
        self.label = get_label(self.element)
        if not self.label:
            self.label = file_rel_to_toc
        
        element.attrib['id'] = f'toc_{toc_order}'
        self.src = file_rel_to_toc + '#' + element.get('id')
        
        self.level = 0
        match self.element.tag:
            case 'h1':
                self.level = 1
            case 'h2':
                self.level = 2
            case 'h3':
                self.level = 3
            case 'h4':
                self.level = 4
            case 'h5':
                self.level = 5
            case 'h6':
                self.level = 6
        
        if self.level == 0:
            match self.element.get('class'):
                case 'title1':
                    self.level = 1
                case 'title2':
                    self.level = 2
                case 'title3':
                    self.level = 3
                case 'title4':
                    self.level = 4
                case 'title5':
                    self.level = 5
                case 'title6':
                    self.level = 6
                case 'book-title':
                    self.level = 1
                case 'title':
                    self.level = 1
                case 'subtitle':
                    self.level = 2
        
    
    def __str__(self):
        lines = [
            'Label: ' + self.label,
            'Src: ' + self.src,
            'Tag: ' + self.element.tag,
            'Level: ' + str(self.level),
        ]
        
        text = '\n'.join(lines)
        
        return text
    
    def new_toc_point(self, parent, order):
        point = etree.Element('{' + ns['ncx'] + '}navPoint')
        label = etree.SubElement(point, '{' + ns['ncx'] + '}navLabel')
        text = etree.SubElement(label, '{' + ns['ncx'] + '}text')
        content = etree.SubElement(point, '{' + ns['ncx'] + '}content')
        
        text.text = self.label
        content.attrib['src'] = self.src
        point.attrib['id'] = str(order)
        point.attrib['playOrder'] = str(order)
        
        parent.append(point)
        self.toc_point = point
        
    def new_nav_point(self, parent):
        li = html.Element('li')
        a = html.Element('a')
        li.append(a)
        
        a.text = self.label
        a.attrib['href'] = self.src
        
        if parent.tag == 'ol':
            ol = parent
        elif parent.tag == 'li':
            ol = parent.find('ol')
            if ol is None:
                ol = html.Element('ol')
                parent.append(ol)
            
        ol.append(li)
        self.nav_point = li


def get_titles(file, toc_parent):
    tree = html.parse(file)
    root = tree.getroot()
    
    titles = []
    file_rel = get_rel(file, toc_parent)
    
    elements = root.xpath('''
        //h1 |
        //h2 |
        //h3 |
        //h4 |
        //h5 |
        //h6 |
        //*[@class="title1"] |
        //*[@class="title2"] |
        //*[@class="title3"] |
        //*[@class="title4"] |
        //*[@class="title5"] |
        //*[@class="title6"] |
        //*[@class="title"] |
        //*[@class="subtitle"] |
        //*[@class="book-title"]
    ''')
    
    counter = 1
    for el in elements:
        if (
            not include_subtitles and 
            (el.tag in ['h4', 'h5', 'h6'] or
            el.get('class') in ['title4', 'title5', 'title6', 'subtitle'])
        ):
            if all_h and el.tag in ['h4', 'h5', 'h6']:
                pass
            else:
                continue
        
        title_obj = Title(el, file_rel, counter)
        titles.append(title_obj)
        counter += 1
    
    tree.write(
        file,
        pretty_print = True,
        xml_declaration = True,
        encoding = 'utf-8'
    )
    
    return titles


def create_toc(toc, titles):
    tree = etree.parse(toc)
    root = tree.getroot()
    nav_map = root.find('ncx:navMap', namespaces = ns)
    
    for child in nav_map.getchildren():
        nav_map.remove(child)
    
    for index, title in enumerate(titles):
        if index == 0:
            parent = nav_map
        elif title.level == 1:
            parent = nav_map
        else:
            last_title = titles[index - 1]
            
            if title.level == last_title.level:
                parent = last_title.toc_point.getparent()
            elif title.level > last_title.level:
                parent = last_title.toc_point
            elif title.level < last_title.level:
                for t in reversed(titles[:index - 1]):
                    if title.level == t.level:
                        parent = t.toc_point.getparent()
                        break
                    
                    elif title.level > t.level:
                        parent = t.toc_point
                        break
        
        title.new_toc_point(parent, index + 1)
    
    
    tree.write(
        toc,
        pretty_print = True,
        xml_declaration = True,
        encoding = 'utf-8'
    )

def create_nav(nav, titles):
    tree = html.parse(nav)
    root = tree.getroot()
    nav_map = root.find('.//nav[@id="toc"]')
    first_ol = nav_map.find('ol')
    if first_ol is None:
        first_ol = html.Element('ol')
        nav_map.append(first_ol)
    
    for child in first_ol.getchildren():
        first_ol.remove(child)
    
    for index, title in enumerate(titles):
        if index == 0:
            parent = first_ol
        elif title.level == 1:
            parent = first_ol
        else:
            last_title = titles[index - 1]
            
            if title.level == last_title.level:
                parent = last_title.nav_point.getparent()
            elif title.level > last_title.level:
                parent = last_title.nav_point
            elif title.level < last_title.level:
                for t in reversed(titles[:index - 1]):
                    if title.level == t.level:
                        parent = t.nav_point.getparent()
                        break
                    
                    elif title.level > t.level:
                        parent = t.nav_point
                        break
        
        title.new_nav_point(parent)
    
    
    tree.write(
        nav,
        pretty_print = True,
        xml_declaration = True,
        encoding = 'utf-8'
    )


def main(temp_path):
    toc_tuple, what_is_it = get_toc(temp_path)
    if what_is_it == 'toc and nav':
        toc = toc_tuple[0]
        nav = toc_tuple[1]
    else:
        toc = toc_tuple[0]
    
    files = get_files_in_spine_order(temp_path)
    titles = []
    for file in files:
        file_titles = get_titles(file, toc.parent)
        titles.extend(file_titles)
    
    match what_is_it:
        case 'toc':
            create_toc(toc, titles)
        case 'nav':
            create_nav(toc, titles)
        case 'toc and nav':
            create_toc(toc, titles)
            create_nav(nav, titles)