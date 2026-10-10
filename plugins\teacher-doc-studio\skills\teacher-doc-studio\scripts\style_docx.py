"""Conservative Word styling for Thai/English teacher reports.

Python 3 + python-docx. Does not convert plain text into semantic headings.
Existing body text, fields and document relationships are preserved.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from collections import Counter

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from docx.text.paragraph import Paragraph
from docx.table import Table
sys.path.insert(0, str(Path(__file__).resolve().parent))
from docx_integrity import preserve_package, compare_packages, write_format_report

PROFILES = {
    'thai': dict(font='Tahoma', size=11.5, title=20, h1=15, line=1.18),
    'english': dict(font='Calibri', size=11.5, title=22, h1=16, line=1.15),
    'bilingual': dict(font='Tahoma', size=11.5, title=20, h1=15, line=1.18),
    'thai-formal': dict(font='TH Sarabun New', size=16, title=28, h1=22, h2=20,
                       h3=18, line=1.0, after=4, table_size=14, caption_size=14, footer_size=14,subtitle_size=16),
}

CONFIG_LIMITS={'size':(8,24),'title':(12,48),'h1':(10,36),'h2':(10,32),
               'h3':(8,28),'line':(1,2),'after':(0,20),'margin_cm':(1,4),
               'table_size':(8,20),'caption_size':(8,20),'footer_size':(8,20),'subtitle_size':(8,24)}


def resolve_config(profile, config_path=None):
    cfg=dict(PROFILES[profile])
    cfg.update(schema_version=1,profile=profile)
    if config_path:
        supplied=json.loads(Path(config_path).read_text(encoding='utf-8'))
        if not isinstance(supplied,dict):
            raise ValueError('Configuration must be a JSON object.')
        unknown=set(supplied)-set(CONFIG_LIMITS)-{'font','schema_version','profile'}
        if unknown:
            raise ValueError('Unknown configuration fields: '+', '.join(sorted(unknown)))
        if supplied.get('schema_version',1)!=1:
            raise ValueError('Unsupported configuration schema version.')
        if supplied.get('profile',profile)!=profile:
            raise ValueError('Configuration profile must match --profile.')
        cfg.update(supplied)
    if not isinstance(cfg['font'],str) or not cfg['font'].strip() or len(cfg['font'])>100:
        raise ValueError('Font must be a non-empty family name.')
    for key,(low,high) in CONFIG_LIMITS.items():
        if key in cfg and (isinstance(cfg[key],bool) or not isinstance(cfg[key],(int,float)) or not low<=cfg[key]<=high):
            raise ValueError(f'Configuration {key} must be between {low} and {high}.')
    return cfg


def font_status(font):
    if sys.platform != 'win32':
        return 'Font availability was not checked on this platform.'
    import winreg
    found=[]
    for hive in (winreg.HKEY_LOCAL_MACHINE,winreg.HKEY_CURRENT_USER):
        try:
            with winreg.OpenKey(hive,r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts') as key:
                for i in range(winreg.QueryInfoKey(key)[1]):
                    found.append(winreg.EnumValue(key,i)[0].lower().split(' (')[0])
        except OSError:
            continue
    return ('Font family confirmed in Windows font registry.' if font.lower() in found
            else 'Requested font was not confirmed in Windows font registry; check substitution in the renderer.')


def snapshot(doc):
    body = doc.element.body
    texts = body.xpath('.//w:t | .//w:instrText | .//w:delText')
    payload = json.dumps([x.text for x in texts], ensure_ascii=False)
    nodes = Counter(x.tag.rsplit('}', 1)[-1] for x in body.iter())
    watched = ('tbl', 'drawing', 'pict', 'hyperlink', 'fldSimple', 'fldChar',
               'footnoteReference', 'endnoteReference', 'commentReference', 'ins', 'del')
    return {'text_sha256': hashlib.sha256(payload.encode('utf-8')).hexdigest(),
            'structures': {k: nodes[k] for k in watched}}


def set_fonts(rpr, name, size):
    fonts = rpr.find(qn('w:rFonts'))
    if fonts is None:
        fonts = OxmlElement('w:rFonts')
        rpr.insert(0, fonts)
    # Remove theme overrides so a theme cannot replace the selected font.
    for attr in list(fonts.attrib):
        if attr.lower().endswith('theme'):
            del fonts.attrib[attr]
    for key in ('ascii', 'hAnsi', 'eastAsia', 'cs'):
        fonts.set(qn('w:' + key), name)
    for key in ('sz', 'szCs'):
        el = rpr.find(qn('w:' + key))
        if el is None:
            el = OxmlElement('w:' + key)
            rpr.append(el)
        el.set(qn('w:val'), str(round(size * 2)))


def set_flag(parent, tag, value=True):
    el = parent.find(qn('w:' + tag))
    if el is None:
        el = OxmlElement('w:' + tag)
        parent.append(el)
    el.set(qn('w:val'), '1' if value else '0')


def format_document(doc, profile, footer_label=None, config=None):
    cfg = config or resolve_config(profile)
    sizes = {'Normal': cfg['size'], 'Body Text': cfg['size'],
             'Title': cfg['title'], 'Subtitle': cfg.get('subtitle_size',11),
             'Heading 1': cfg['h1'], 'Heading 2': cfg.get('h2',13), 'Heading 3': cfg.get('h3',11.5),
             'List Bullet': cfg['size'], 'List Number': cfg['size'],
             'Quote': cfg['size'], 'Caption': cfg.get('caption_size',10)}
    for name, size in sizes.items():
        if name not in doc.styles:
            continue
        style = doc.styles[name]
        set_fonts(style.element.get_or_add_rPr(), cfg['font'], size)
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.font.bold = name == 'Title' or name.startswith('Heading')
        style.font.italic = name == 'Quote' and profile == 'english'
        set_flag(style.element.get_or_add_rPr(), 'bCs', name == 'Title' or name.startswith('Heading'))
        set_flag(style.element.get_or_add_rPr(), 'iCs', name == 'Quote' and profile == 'english')
        for char_spacing in list(style.element.rPr.findall(qn('w:spacing'))):
            style.element.rPr.remove(char_spacing)
        if name in ('Title', 'Subtitle') or name.startswith('Heading'):
            ppr = style.element.pPr
            if ppr is not None:
                for border in list(ppr.findall(qn('w:pBdr'))):
                    ppr.remove(border)
        pf = style.paragraph_format
        pf.line_spacing = cfg['line']
        pf.space_after = Pt(cfg.get('after',7))
        pf.widow_control = True
        if name.startswith('Heading'):
            pf.keep_with_next = True
            pf.space_before = Pt(14 if name == 'Heading 1' else 10)
            pf.space_after = Pt(6 if name == 'Heading 1' else 5)
        elif name == 'Title':
            pf.keep_with_next = True
            pf.space_after = Pt(8)
        elif name == 'Subtitle':
            pf.keep_with_next = True
            pf.space_after = Pt(12)
        elif name == 'Quote':
            pf.left_indent = Cm(0.6)
            pf.right_indent = Cm(0.3)

    # Only normalise page geometry for a single, portrait section.
    # Multi-section and landscape source layouts may be intentional.
    if len(doc.sections) == 1 and doc.sections[0].page_width < doc.sections[0].page_height:
        sec = doc.sections[0]
        sec.page_width = Cm(21)
        sec.page_height = Cm(29.7)
        sec.top_margin = sec.bottom_margin = Cm(cfg.get('margin_cm',2.2))
        sec.left_margin = sec.right_margin = Cm(cfg.get('margin_cm',2.2))
        sec.header_distance = sec.footer_distance = Cm(0.9)

    for node in doc.element.body.xpath('.//w:p'):
        if any(x.tag in (qn('w:txbxContent'),qn('w:drawing'),qn('w:pict')) for x in node.iterancestors()):
            continue
        para = Paragraph(node, doc._body)
        name = para.style.name if para.style else 'Normal'
        if name not in sizes:
            # Preserve special source styles such as equations or captions.
            continue
        pf = para.paragraph_format
        pf.widow_control = True
        pf.line_spacing = cfg['line']
        if not any(x.tag == qn('w:tc') for x in node.iterancestors()):
            pf.space_after = Pt(cfg.get('after',7))
        if name.startswith('Heading') or name in ('Title', 'Subtitle'):
            pf.keep_with_next = True
            pf.space_before = Pt(14 if name == 'Heading 1' else 10 if name.startswith('Heading') else 0)
            pf.space_after = Pt(6 if name.startswith('Heading') else 8 if name == 'Title' else 12)
        in_table = any(x.tag == qn('w:tc') for x in node.iterancestors())
        size = min(sizes[name], cfg.get('table_size',11)) if in_table else sizes[name]
        for run in node.xpath('.//w:r'):
            if not run.xpath('./w:t'):
                continue
            font = cfg['font']
            text = ''.join(run.xpath('.//w:t/text()'))
            if profile == 'english' and any('\u0e00' <= c <= '\u0e7f' for c in text):
                font = 'Tahoma'
            set_fonts(run.get_or_add_rPr(), font, size)

    for table_node in doc.element.body.xpath('.//w:tbl'):
        table=Table(table_node,doc._body)
        for index, row in enumerate(table.rows):
            props = row._tr.get_or_add_trPr()
            set_flag(props, 'cantSplit')
            if index == 0:
                set_flag(props, 'tblHeader')
                for cell in row.cells:
                    tcpr = cell._tc.get_or_add_tcPr()
                    shd = tcpr.find(qn('w:shd'))
                    if shd is None:
                        shd = OxmlElement('w:shd')
                        tcpr.append(shd)
                    shd.set(qn('w:fill'), 'F1F3F5')
                    for p in cell.paragraphs:
                        for r in p.runs:
                            r.bold = True
                            set_flag(r._r.get_or_add_rPr(),'bCs',True)
        # Cell padding is table-level; preserve source-specific cell margins.
        props = table._tbl.tblPr
        margins = props.find(qn('w:tblCellMar'))
        if margins is None:
            margins = OxmlElement('w:tblCellMar')
            props.append(margins)
            for side in ('top', 'left', 'bottom', 'right'):
                el = OxmlElement('w:' + side)
                el.set(qn('w:w'), '110')
                el.set(qn('w:type'), 'dxa')
                margins.append(el)

    footer_added = False
    if footer_label and len(doc.sections) == 1:
        sec = doc.sections[0]
        footer = sec.footer
        existing = bool(footer._element.xpath('.//w:t | .//w:fldChar | .//w:fldSimple | .//w:drawing'))
        if not existing and not sec.different_first_page_header_footer and not doc.settings.odd_and_even_pages_header_footer:
            p = footer.paragraphs[0]
            p.style = doc.styles['Normal']
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1
            p.paragraph_format.tab_stops.add_tab_stop(sec.page_width-sec.left_margin-sec.right_margin, 2)
            label = p.add_run(footer_label + '\t')
            set_fonts(label._r.get_or_add_rPr(), cfg['font'], cfg.get('footer_size',9))
            field = OxmlElement('w:fldSimple')
            field.set(qn('w:instr'), 'PAGE')
            run = OxmlElement('w:r')
            text = OxmlElement('w:t')
            text.text = '1'
            run.append(text)
            set_fonts(run.get_or_add_rPr(), cfg['font'], cfg.get('footer_size',9))
            field.append(run)
            p._p.append(field)
            footer_added = True
    return {'profile': profile, 'footer_added': footer_added,
            'added_footer_part':str(doc.sections[0].footer.part.partname) if footer_added else None,
            'multi_section_preserved': len(doc.sections) != 1}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--profile', choices=PROFILES, default='thai')
    parser.add_argument('--footer-label')
    parser.add_argument('--config',type=Path)
    parser.add_argument('--export-config',type=Path)
    parser.add_argument('--report',type=Path)
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        parser.error('Use a separate output path; input must remain intact.')
    if args.output.exists():
        parser.error('Output already exists; select a new output path.')
    cfg=resolve_config(args.profile,args.config)
    report=args.report or args.output.with_suffix('.format-report.md')
    audit_path=args.output.with_suffix('.audit.json')
    for sidecar in (report,audit_path,args.export_config):
        if sidecar and (sidecar.exists() or sidecar.resolve() in (args.input.resolve(),args.output.resolve())):
            parser.error('Report/config output must be a new, separate file.')
    doc = Document(args.input)
    before = snapshot(doc)
    details = format_document(doc, args.profile, args.footer_label,cfg)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temp_paths=[]
    try:
        for _ in range(2):
            fd,name=tempfile.mkstemp(suffix='.docx',prefix='.tds-',dir=args.output.parent)
            os.close(fd); temp_paths.append(Path(name))
        doc.save(temp_paths[0])
        preserve_package(args.input,temp_paths[0],temp_paths[1],details['added_footer_part'])
        after = snapshot(Document(temp_paths[1]))
        package_check=compare_packages(args.input,temp_paths[1],details['added_footer_part'])
        if before != after or not package_check['passed']:
            raise RuntimeError('Preservation check failed: '+ '; '.join(package_check['errors']))
        # Exclusive creation avoids silently replacing another user's output.
        with args.output.open('xb') as stream:
            stream.write(temp_paths[1].read_bytes())
    finally:
        for path in temp_paths:
            if path.exists(): path.unlink()
    review_items=[font_status(cfg['font'])]
    if len(doc.sections)>1:
        review_items.append('Multiple sections: original page geometry retained; inspect each section.')
    complex_tags={'sdt':'content controls','ins':'tracked insertions','del':'tracked deletions',
                  'object':'embedded objects','txbxContent':'text boxes'}
    for tag,label in complex_tags.items():
        if doc.element.body.xpath('.//w:'+tag):
            review_items.append('Review '+label+' in the native editor; content/package structure was retained.')
    audit = dict(details, input=args.input.name, output=args.output.name,
                 before=before, after=after, structural_check='passed',
                 configuration=cfg,package_check=package_check,review_items=review_items,
                 visual_check='not performed by this script')
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
    report.parent.mkdir(parents=True,exist_ok=True)
    write_format_report(report,audit)
    if args.export_config:
        args.export_config.parent.mkdir(parents=True,exist_ok=True)
        args.export_config.write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'output': str(args.output), 'structural_check': 'passed'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
