from __future__ import annotations
import json
from pathlib import Path
from urllib.parse import urlparse
from app.models.menu import Menu, Section
from config import DATA_FILE

class ContentError(ValueError):
    """Dokumen konten tidak sesuai skema."""

class ContentRepository:
    def __init__(self,path:Path=DATA_FILE):
        try: raw=json.loads(path.read_text(encoding='utf-8'))
        except (OSError,json.JSONDecodeError) as e:raise ContentError(f'Gagal membaca data konten: {e}') from e
        entries=raw.get('menus',[]) if isinstance(raw,dict) else []
        if len(entries)!=10:raise ContentError('Data harus memuat tepat 10 menu.')
        self.menus={}
        for n,d in enumerate(entries,1):
            try:
                if d['id']!=n or d['gesture']!=n:raise ContentError(f'Nomor menu {n} tidak valid')
                if not d['sections'] or not d['source_urls']:raise ContentError(f'Bagian atau sumber menu {n} kosong')
                for url in d['source_urls']:
                    u=urlparse(url)
                    if u.scheme!='https' or not u.netloc:raise ContentError(f'URL menu {n} tidak aman')
                for key in ('title','subtitle','intro','summary','narration_text','narration_id'):
                    if not isinstance(d.get(key),str) or not d[key].strip():
                        raise ContentError(f'Kolom {key} pada menu {n} kosong')
                secs=tuple(Section(**{k:v for k,v in s.items() if k in ('title','body','asset')}) for s in d['sections'])
                if any(not s.title or not s.body for s in secs):raise ContentError(f'Bagian menu {n} kosong')
                menu=Menu(id=n,gesture=n,title=d['title'],subtitle=d['subtitle'],intro=d['intro'],
                          sections=secs,summary=d['summary'],narration_text=d['narration_text'],
                          narration_id=d['narration_id'],visual_assets=tuple(d.get('visual_assets',[])),
                          source_urls=tuple(d['source_urls']),last_verified_at=d.get('last_verified_at'),
                          verification_status=d.get('verification_status','DRAF_BELUM_DISAHKAN'),
                          validation_note=d.get('validation_note',''),
                          requires_current_information_check=d.get('requires_current_information_check',False))
                self.menus[n]=menu
            except (KeyError,TypeError) as e:raise ContentError(f'Skema menu {n} tidak valid: {e}') from e

    def get(self,number:int)->Menu:
        return self.menus[number]
