"""Ekstraksi terkontrol draf 2 November 2026 menjadi JSON. Tidak menambah fakta."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from docx import Document

TITLES = ['Profil FILKOM', 'Fasilitas', 'Program Studi', 'Laboratorium',
          'Layanan Akademik', 'Penerimaan Mahasiswa', 'Beasiswa',
          'Kemahasiswaan', 'Penelitian & Pengabdian', 'Kontak & Lokasi']
DYNAMIC = {3, 5, 6, 7, 8, 10}

def extract(path: Path) -> list[dict]:
    doc = Document(path)
    paragraphs = [p.text.strip() for p in doc.paragraphs]
    src = {}
    for p in paragraphs:
        m = re.match(r'\[(S\d+)\].*?(https?://\S+)', p)
        if m:
            src[m.group(1)] = m.group(2)
    subs = {}
    for table in doc.tables:
        if len(table.rows) == 1 and len(table.columns) == 1:
            s = table.cell(0, 0).text.strip()
            if s.startswith('Teks kartu menu:'):
                subs[len(subs)+1] = s.split(':',1)[1].strip()
    entries = []
    for number in range(1,11):
        key = re.compile(r'^MENU\s+0?'+str(number)+r'\s*\|')
        start = next(i for i,p in enumerate(paragraphs) if key.match(p))
        stop = next((i for i in range(start+1, len(paragraphs)) if re.match(r'^MENU\s+\d+\s*\|', paragraphs[i])), len(paragraphs))
        block = paragraphs[start:stop]
        def after(label):
            j = block.index(label)
            return block[j+1]
        sect_start = block.index('Konten pada layar detail')+1
        sect_stop = block.index('Ringkasan yang ditampilkan')
        sections = []
        for s in block[sect_start:sect_stop]:
            if not s: continue
            a = re.split(r'\s+—\s+', s, maxsplit=1)
            if len(a)!=2: raise ValueError(f'Bagian tidak valid: {s}')
            sections.append({'title':a[0].strip(), 'body':a[1].strip(), 'asset':None})
        source_line = next(p for p in block if p.startswith('Sumber rujukan:'))
        codes = re.findall(r'\[(S\d+)\]', source_line)
        narr = after('Naskah narasi Text-to-Speech').strip().strip('“”').strip()
        validation = next(p.split(':',1)[1].strip() for p in block if p.startswith('Catatan validasi:'))
        entries.append({
            'id':number,'gesture':number,'title':TITLES[number-1],
            'subtitle':subs[number], 'intro':block[1], 'sections':sections,
            'summary':after('Ringkasan yang ditampilkan'),
            'narration_id':f'menu_{number:02d}', 'narration_text':narr,
            'visual_assets':[], 'visual_guidance':after('Petunjuk visual & implementasi'),
            'source_codes':codes, 'source_urls':[src[c] for c in codes],
            'last_verified_at':None,
            'source_draft_date':'2026-11-02',
            'verification_status':'DRAF_BELUM_DISAHKAN',
            'validation_note':validation,
            'requires_current_information_check':number in DYNAMIC,
        })
    return entries

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('docx',type=Path)
    ap.add_argument('--output',type=Path, default=Path('data/menus.json'))
    args=ap.parse_args()
    result={'metadata':{'document':'Rancangan Konten Aplikasi 10 Menu Layanan Informasi Cerdas FILKOM UB',
             'version':'Rancangan 1.0', 'draft_date':'2026-11-02',
             'editorial_status':'DRAF PENELITIAN; bukan materi publikasi resmi FILKOM UB'},'menus':extract(args.docx)}
    args.output.parent.mkdir(exist_ok=True,parents=True)
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f'{len(result["menus"])} menu ditulis: {args.output}')

if __name__=='__main__':main()
