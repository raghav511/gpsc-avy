"""Strip authoring and tool details from every downloadable PDF's metadata (title and subject are kept)."""
import os, sys, pikepdf
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'content', 'pdfs')
for f in sorted(os.listdir(D)):
    if not f.endswith('.pdf'):
        continue
    p = os.path.join(D, f)
    with pikepdf.open(p, allow_overwriting_input=True) as pdf:
        info = pdf.docinfo
        changed = False
        for k in ('/Author', '/Creator', '/Producer', '/Keywords'):
            if k in info:
                del info[k]; changed = True
        try:
            with pdf.open_metadata(set_pikepdf_as_editor=False) as m:
                for k in ('dc:creator', 'xmp:CreatorTool', 'pdf:Producer', 'pdf:Keywords'):
                    if k in m: del m[k]; changed = True
        except Exception:
            pass
        if changed:
            pdf.save(p)
            print('cleaned', f)
