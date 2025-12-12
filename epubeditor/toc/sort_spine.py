from rich import print
from epubeditor.namespaces import namespaces
from epubeditor.open_book.files_operations import get_rel

debug = False

def raw_to_src(src_in_toc_raw, toc_parent, opf_parent):
    src_in_toc = []
    for src in src_in_toc_raw:
        if '#' in src:
            index = src.find('#')
            src = src[:index]
        
        src_path = toc_parent / src
        src_rel = get_rel(src_path.resolve(), opf_parent)
        
        if src_rel not in src_in_toc:
            src_in_toc.append(src_rel)
    
    if debug:
        print('src raw')
        print(src_in_toc_raw)
        print('src')
        print(src_in_toc)
    
    return src_in_toc

def get_item_ids(src_in_toc, items, itemrefs_all):
    item_id = []
    for src in src_in_toc:
        for item in items:
            if src in item.attrib['href']:
                item_id.append(item.attrib['id'])
                break
    
    item_id_old = []
    for i in itemrefs_all:
        if i.get('idref') in item_id:
            item_id_old.append(i.get('idref'))
    return item_id, item_id_old

def get_ref_between_xpath(spine, item_id_old):
    ref_between = {}
    for i, v in enumerate(item_id_old):
        if v != item_id_old[-1]:
            items = spine.xpath(
                f'//opf:itemref[@idref="{v}"]/following-sibling::opf:itemref[following-sibling::opf:itemref[@idref="{item_id_old[i + 1]}"]]', 
                namespaces = namespaces
            )
        else:
            items = spine.xpath(
                f'//opf:itemref[@idref="{v}"]/following-sibling::opf:itemref', 
                namespaces = namespaces
            )
        
        if items:
            ref_between[v] = items
    return ref_between

def get_ref_between(item_id_old, itemrefs_all):
    ref_between = {}
    for i, v in enumerate(item_id_old):
        items = []
        to_delete = []
        if v != item_id_old[-1]:
            is_item_finded = False
            for index, ref in enumerate(itemrefs_all):
                if v == ref.attrib['idref']:
                    is_item_finded = True
                    continue
                if is_item_finded:
                    if item_id_old[i + 1] != ref.attrib['idref']:
                        items.append(ref)
                        to_delete.append(index)
                    else:
                        break
            
            for i in reversed(to_delete):
                del itemrefs_all[i]
            
        else:
            # Обработка последнего колышка в списке
            is_item_finded = False
            for index, ref in enumerate(itemrefs_all):
                if v == ref.attrib['idref']:
                    is_item_finded = True
                    continue
                if is_item_finded:
                    if ref.attrib['idref'] not in item_id_old:
                        items.append(ref)
                    else:
                        break
            
        if items:
            ref_between[v] = items
    return ref_between

def main(opf_root, src_in_toc):
    manifest = opf_root.xpath('//opf:manifest', namespaces = namespaces)
    spine = opf_root.xpath('//opf:spine', namespaces = namespaces)
    if manifest and spine:
        manifest = manifest[0]
        spine = spine[0]
    else:
        print("Error while parsing spine in .opf file!")
        return
    
    items = manifest.xpath('./opf:item', namespaces = namespaces)
    itemrefs_all = spine.xpath('./opf:itemref', namespaces = namespaces)
    
    item_id, item_id_old = get_item_ids(src_in_toc, items, itemrefs_all)
    
    itemrefs = []
    for i in item_id:
        for item in itemrefs_all:
            if i == item.attrib['idref']:
                itemrefs.append(item)
    
    ref_between = get_ref_between_xpath(spine, item_id_old)
    if not ref_between:
        ref_between = get_ref_between(item_id_old, itemrefs_all)
    
    if debug:
        print('-------')
        print('item_id')
        print(item_id)
        
        if item_id == item_id_old:
            print('item_id and item_id_old is equal')
        else:
            print('-----------')
            print('item_id_old')
            print(item_id_old)
        
        print('------------')
        print('itemrefs_all')
        for item in itemrefs_all:
            print(item.get('idref'))
        
        print('-----------')
        print('ref_between')
        for k, value in ref_between.items():
            print(k)
            for v in value:
                print('\t', v.attrib['idref'])
        
        print('-----')
        print('new order')
    
    for item in itemrefs:
        key = item.attrib['idref']
        if debug:
            print(key)
        
        spine.append(item)
        
        if key in ref_between:
            for ref in ref_between[key]:
                if debug:
                    print(ref.attrib['idref'])
                
                spine.append(ref)

if __name__ == "__main__":
    print("This is just module, try to run cli.py")
