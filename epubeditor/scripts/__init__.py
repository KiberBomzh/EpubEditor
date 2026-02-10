from .toc_from_titles import main as toc_from_titles
from .split_by_titles import main as split_by_titles
from .clean_doubled_xml_declarations import main as clean_doubled_xml_declarations
from .generate_order_for_toc import main as generate_order_for_toc


__all__ = [
    'toc_from_titles',
    'split_by_titles',
    'clean_doubled_xml_declarations',
    'generate_order_for_toc'
]