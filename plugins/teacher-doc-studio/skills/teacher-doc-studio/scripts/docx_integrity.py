"""Preserve the source DOCX package while applying narrowly scoped formatting.

Original implementation. No external formatter source is bundled or executed.
"""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
PARSER = etree.XMLParser(resolve_entities=False, no_network=True)
TEXT_TAGS = {f'{{{W}}}{n}' for n in ('t','delText','instrText')} | {f'{{{M}}}t'}
STRUCTURE_TAGS = {f'{{{W}}}{n}' for n in ('tbl','drawing','pict','object','hyperlink',
    'fldSimple','fldChar','footnoteReference','endnoteReference','commentReference',
    'commentRangeStart','commentRangeEnd','sdt','ins','del')} | {f'{{{M}}}oMath'}


def parts(path):
    with ZipFile(path) as z:
        if len(z.namelist()) != len(set(z.namelist())):
            raise ValueError('DOCX contains duplicate package part names.')
        bad = z.testzip()
        if bad:
            raise ValueError('Corrupt DOCX package part: ' + bad)
        return {n:z.read(n) for n in z.namelist()}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def merge_registry(original, generated, relationship=False):
    """Retain original content-type/relationship entries and add new ones."""
    old=etree.fromstring(original, PARSER)
    new=etree.fromstring(generated, PARSER)
    def key(el):
        return el.get('Id') if relationship else (el.tag, el.get('PartName') or el.get('Extension'))
    entries={key(el):el for el in old}
    for el in new:
        k=key(el)
        if k in entries:
            if dict(entries[k].attrib) != dict(el.attrib):
                raise ValueError('Existing package registry entry changed: ' + str(k))
        else:
            old.append(el)
    return etree.tostring(old, encoding='UTF-8', xml_declaration=True, standalone=True)


def preserve_package(source, generated, destination, added_footer=None):
    """Retain every original part, including parts outside python-docx's model."""
    original=parts(source); formatted=parts(generated)
    result=dict(original)
    editable={'word/document.xml','word/styles.xml'}
    if added_footer:
        editable.add(added_footer.lstrip('/'))
    for name in editable:
        if name in formatted:
            result[name]=formatted[name]
    for name,data in formatted.items():
        if name not in result:
            result[name]=data
    for name,relationship in [('[Content_Types].xml',False),('word/_rels/document.xml.rels',True)]:
        if name in original and name in formatted:
            result[name]=merge_registry(original[name],formatted[name],relationship)
    with ZipFile(destination,'w',ZIP_DEFLATED) as z:
        for name,data in result.items():
            z.writestr(name,data)


def semantic_snapshot(data):
    tree=etree.fromstring(data,PARSER)
    # Element order and attributes carry anchors, field instructions, IDs,
    # equations, numbering references and embedded-object relationships.
    events=[]
    protected_subtrees={f'{{{W}}}{n}' for n in ('drawing','pict','object')} | {f'{{{M}}}oMath',f'{{{W}}}numPr'}
    for el in tree.iter():
        if el.tag in TEXT_TAGS:
            events.append((el.tag,el.text))
        elif el.tag in STRUCTURE_TAGS:
            events.append((el.tag,dict(el.attrib)))
        if el.tag in protected_subtrees:
            events.append(('protected_subtree',etree.tostring(el,method='c14n').decode()))
    payload=json.dumps(events,ensure_ascii=False,sort_keys=True)
    return digest(payload.encode('utf-8'))


def compare_packages(source, output, added_footer=None):
    before=parts(source); after=parts(output)
    allowed={'word/document.xml','word/styles.xml','[Content_Types].xml','word/_rels/document.xml.rels'}
    if added_footer:
        allowed.add(added_footer.lstrip('/'))
    errors=[]
    lost=sorted(set(before)-set(after))
    if lost:
        errors.append('Package parts were lost: ' + ', '.join(lost))
    changed=sorted(n for n in before if n in after and before[n]!=after[n])
    for name in changed:
        if name not in allowed:
            errors.append('Protected package part changed: ' + name)
    if 'word/document.xml' in before and 'word/document.xml' in after:
        if semantic_snapshot(before['word/document.xml']) != semantic_snapshot(after['word/document.xml']):
            errors.append('Body text, field/annotation anchors, numbering, or structural order changed.')
    # Check original registry entries, rather than requiring byte equality.
    for name,relationship in [('[Content_Types].xml',False),('word/_rels/document.xml.rels',True)]:
        if name in before and name in after:
            try:
                merge_registry(before[name],after[name],relationship)
                a=etree.fromstring(before[name],PARSER); b=etree.fromstring(after[name],PARSER)
                key=lambda el: el.get('Id') if relationship else (el.tag,el.get('PartName') or el.get('Extension'))
                bkeys={key(el) for el in b}
                if any(key(el) not in bkeys for el in a):
                    errors.append('Original registry entry was removed: ' + name)
            except ValueError as exc:
                errors.append(str(exc))
    return {'passed':not errors,'errors':errors,'original_part_count':len(before),
            'output_part_count':len(after),'changed_parts':changed,
            'added_parts':sorted(set(after)-set(before)),
            'protected_parts_checked':len(set(before)-allowed),
            'source_sha256':digest(Path(source).read_bytes()),
            'output_sha256':digest(Path(output).read_bytes())}


def write_format_report(path, audit):
    checks=audit['package_check']
    cfg=audit['configuration']
    lines=['# รายงานตรวจรูปแบบ Word / Word format check','',
        f"- Input: {audit['input']}",f"- Output: {audit['output']}",
        f"- Profile: {audit['profile']}",f"- Body font: {cfg['font']} {cfg['size']} pt",
        f"- Preservation check: {'PASS' if checks['passed'] else 'FAIL'}",
        f"- Protected package parts checked: {checks['protected_parts_checked']}",
        '- Visual layout: not verified by the formatting script; render and inspect every page.',
        '', '## What changed','']
    lines += ['- '+n for n in checks['changed_parts']]
    lines += ['', '## Items requiring review','']
    lines += ['- '+n for n in audit['review_items']] or ['- None identified structurally.']
    lines += ['', 'This report checks package integrity and formatting decisions. It does not certify institutional requirements or page appearance.','']
    Path(path).write_text('\n'.join(lines),encoding='utf-8')
