import docx
import os
import json

def extract_doc_structure(filepath, outpath):
    try:
        doc = docx.Document(filepath)
    except Exception as e:
        print(f"Failed to open {filepath}: {e}")
        return

    content = []
    
    # helper for docx block level iteration
    from docx.document import Document
    from docx.oxml.table import CT_Tbl
    from docx.oxml.text.paragraph import CT_P
    from docx.table import _Cell, Table
    from docx.text.paragraph import Paragraph

    def iter_block_items(parent):
        if isinstance(parent, Document):
            parent_elm = parent.element.body
        elif isinstance(parent, _Cell):
            parent_elm = parent._tc
        else:
            raise ValueError("something's not right")

        for child in parent_elm.iterchildren():
            if isinstance(child, CT_P):
                yield Paragraph(child, parent)
            elif isinstance(child, CT_Tbl):
                yield Table(child, parent)

    blocks = []
    for count, block in enumerate(iter_block_items(doc)):
        if isinstance(block, Paragraph):
            if block.text.strip():
                blocks.append({"type": "paragraph", "index": count, "text": block.text.strip()})
        elif isinstance(block, Table):
            table_data = []
            for row in block.rows:
                row_data = []
                for cell in row.cells:
                    row_data.append(cell.text.strip())
                table_data.append(row_data)
            blocks.append({"type": "table", "index": count, "data": table_data})
            
    with open(outpath, 'w', encoding='utf-8') as f:
        json.dump(blocks, f, indent=2)
    print(f"Extracted {filepath} to {outpath}")

tech_doc = r"c:\Users\ADMIN\OneDrive\Documents\SAD_System_files\technopath\technopath_pwa\version4_technopath\Technopath -Chapter 1 and Chapter 3 -  Final(2) (Repaired).docx"
attendx_doc = r"c:\Users\ADMIN\OneDrive\Documents\SAD_System_files\technopath\technopath_pwa\version4_technopath\ATTENDX-EXAMPLE-DOCUMENT.docx"

extract_doc_structure(tech_doc, 'technopath_doc.json')
extract_doc_structure(attendx_doc, 'attendx_doc.json')
