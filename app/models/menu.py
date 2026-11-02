from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Section:
    title:str
    body:str
    asset:str|None=None

@dataclass(frozen=True)
class Menu:
    id:int
    gesture:int
    title:str
    subtitle:str
    intro:str
    sections:tuple[Section,...]
    summary:str
    narration_text:str
    narration_id:str
    visual_assets:tuple[str,...]=()
    source_urls:tuple[str,...]=()
    last_verified_at:str|None=None
    verification_status:str='DRAF_BELUM_DISAHKAN'
    validation_note:str=''
    requires_current_information_check:bool=False
