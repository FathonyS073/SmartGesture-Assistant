"""Lokasi, pengaturan dan batas konfigurasi aplikasi."""
from __future__ import annotations
import json
import os
from dataclasses import asdict, dataclass, fields
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT/'data'/'menus.json'
MODEL_FILE = ROOT/'assets'/'models'/'hand_landmarker.task'
MODEL_URL = ('https://storage.googleapis.com/mediapipe-models/hand_landmarker/'
             'hand_landmarker/float16/1/hand_landmarker.task')
CACHE_DIR = Path(os.environ.get('FILKOM_CACHE_DIR',str(Path.home()/'.cache'/'filkom-gesture-info'/'audio')))
CONFIG_FILE = Path(os.environ.get('FILKOM_CONFIG',str(Path.home()/'.config'/'filkom-gesture-info'/'settings.json')))
LOG_FILE = Path(os.environ.get('FILKOM_LOG',str(Path.home()/'.local'/'state'/'filkom-gesture-info'/'app.log')))
VOICES = ('id-ID-GadisNeural','id-ID-ArdiNeural')

@dataclass
class Settings:
    camera_index: int=0
    stability_seconds: float=0.8
    min_frames: int=4
    min_confidence: float=0.55
    volume: int=80
    voice: str='id-ID-GadisNeural'
    speech_rate: int=0
    mirror_preview: bool=True
    show_landmarks: bool=False
    debug: bool=False

    def validate(self):
        self.camera_index=max(0,min(12,int(self.camera_index)))
        self.stability_seconds=max(0.3,min(3.,float(self.stability_seconds)))
        self.min_frames=max(2,min(20,int(self.min_frames)))
        self.min_confidence=max(.3,min(.95,float(self.min_confidence)))
        self.volume=max(0,min(100,int(self.volume)))
        if self.voice not in VOICES:self.voice=VOICES[0]
        self.speech_rate=max(-40,min(40,int(self.speech_rate)))
        self.mirror_preview=bool(self.mirror_preview)
        self.show_landmarks=bool(self.show_landmarks)
        self.debug=bool(self.debug)
        return self

def load_settings(path:Path=CONFIG_FILE)->Settings:
    try:
        raw=json.loads(path.read_text(encoding='utf-8'))
        allowed={f.name for f in fields(Settings)}
        return Settings(**{k:v for k,v in raw.items() if k in allowed}).validate()
    except (FileNotFoundError,ValueError,TypeError,OSError):
        return Settings()

def save_settings(s:Settings,path:Path=CONFIG_FILE)->None:
    s.validate()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp=path.with_suffix('.tmp')
    tmp.write_text(json.dumps(asdict(s),indent=2,ensure_ascii=False),encoding='utf-8')
    os.replace(tmp,path)
