from lxml import etree

from epubeditor.namespaces import namespaces as ns


opf_path = 'content.opf'
toc_path = 'toc.ncx'

def create_container(temp_path):
    meta_inf = temp_path / 'META-INF'
    container_path = meta_inf / 'container.xml'
            
    meta_inf.mkdir()
    container_path.touch()
    
    
    # Пространство имён для container
    CONTAINER_NS = "urn:oasis:names:tc:opendocument:xmlns:container"
    
    # Создаем корневой элемент с правильным пространством имён
    container = etree.Element(
        "{%s}container" % CONTAINER_NS,
        version="1.0",
        nsmap={None: CONTAINER_NS}  # Основное пространство имён
    )
    
    # Добавляем rootfiles
    rootfiles = etree.SubElement(container, "{%s}rootfiles" % CONTAINER_NS)
    
    # Добавляем rootfile (указывает на content.opf)
    rootfile = etree.SubElement(rootfiles, "{%s}rootfile" % CONTAINER_NS)
    rootfile.set("full-path", opf_path)  # или "EPUB/content.opf" для EPUB3
    rootfile.set("media-type", "application/oebps-package+xml")
    
    # Создаем ElementTree и записываем файл
    tree = etree.ElementTree(container)
    
    # Сохраняем с правильными параметрами
    tree.write(
        container_path,
        encoding="UTF-8",
        xml_declaration=True,
        pretty_print=True
    )


def create_opf(temp_path, new_meta, generate_sort):
    opf = temp_path / opf_path
    opf.touch()
    
    OPF_NS = ns['opf']
    DC_NS = ns['dc']
    
    # Создаем корневой элемент с атрибутами и nsmap
    package = etree.Element(
        "{%s}package" % OPF_NS,
        version="2.0",
        unique_identifier="book-id",
        nsmap={
            None: OPF_NS,
            'dc': DC_NS,
            'dcterms': "http://purl.org/dc/terms/"
        }
    )
    
    # Добавляем метаданные
    metadata = etree.SubElement(package, "{%s}metadata" % OPF_NS)
    
    title = etree.SubElement(metadata, '{%s}title' % DC_NS)
    title.text = new_meta['title'] if new_meta['title'] is not None else 'Merged book'
    
    if new_meta['author'] is not None:
        for author in new_meta['author']:
            creator = etree.SubElement(metadata, '{%s}creator' % DC_NS)
            creator.text = author
    
    if new_meta['language'] is not None:
        for lang in new_meta['language']:
            language = etree.SubElement(metadata, '{%s}language' % DC_NS)
            language.text = lang
    
    if new_meta['series'] is not None:
        series = etree.SubElement(metadata, '{%s}meta' % OPF_NS)
        series.attrib['name'] = 'calibre:series'
        series.attrib['content'] = new_meta['series']
        
        if new_meta['series_index'] is not None:
            series_index = etree.SubElement(metadata, '{%s}meta' % OPF_NS)
            series_index.attrib['name'] = 'calibre:series_index'
            series_index.attrib['content'] = new_meta['series_index']
    
    
    if generate_sort:
        from epubeditor.metadata_editor.create_sort import createSort
        createSort(package)
    
    
    # Добавляем manifest
    manifest = etree.SubElement(package, "{%s}manifest" % OPF_NS)
    
    toc_id = 'ncx'
    item_toc = etree.SubElement(manifest, '{%s}item' % OPF_NS)
    item_toc.attrib['href'] = toc_path
    item_toc.attrib['id'] = toc_id
    item_toc.attrib['media-type'] = 'application/x-dtbncx+xml'
    
    # Добавляем spine
    spine = etree.SubElement(package, "{%s}spine" % OPF_NS)
    spine.attrib['toc'] = toc_id
    
    # Записываем в файл
    tree = etree.ElementTree(package)
    tree.write(
        opf,
        encoding="UTF-8",
        xml_declaration=True
    )
    
    return opf


def create_toc(temp_path, title):
    toc = temp_path / toc_path
    toc.touch()
        
    # Пространства имён для NCX
    NCX_NS = ns['ncx']
    
    # Создаем корневой элемент с правильным пространством имён
    ncx = etree.Element(
        "{%s}ncx" % NCX_NS,
        version="2005-1",
        nsmap={None: NCX_NS}
    )
    
    # Добавляем head
    head = etree.SubElement(ncx, "{%s}head" % NCX_NS)
    
    # Добавляем meta элементы в head
    for name, content in [
        ("dtb:depth", "1"),
        ("dtb:totalPageCount", "0"),
        ("dtb:maxPageNumber", "0")
    ]:
        meta = etree.SubElement(head, "{%s}meta" % NCX_NS)
        meta.set("name", name)
        meta.set("content", content)
    
    # Добавляем docTitle
    docTitle = etree.SubElement(ncx, "{%s}docTitle" % NCX_NS)
    text = etree.SubElement(docTitle, "{%s}text" % NCX_NS)
    text.text = "Merged book" if title is None else title
    
    # Добавляем navMap
    etree.SubElement(ncx, "{%s}navMap" % NCX_NS)
    
    # Записываем в файл
    tree = etree.ElementTree(ncx)
    tree.write(
        toc,
        encoding="UTF-8",
        xml_declaration=True
    )
    
    return toc
