"""MediaPipe Tasks HandLandmarker VIDEO mode; 2 hands, 21 points each."""
from __future__ import annotations
import logging
import time
import urllib.request
from pathlib import Path
from config import MODEL_FILE, MODEL_URL
from app.services.gesture_classifier import Point, HandObservation
LOG=logging.getLogger(__name__)

class LandmarkEngine:
    def __init__(self,model_path:Path=MODEL_FILE,download_if_missing:bool=True):
        if not model_path.exists() and download_if_missing:
            model_path.parent.mkdir(parents=True,exist_ok=True)
            temp=model_path.with_suffix('.download')
            try:
                with urllib.request.urlopen(MODEL_URL,timeout=15) as r,open(temp,'wb') as f:
                    import shutil
                    shutil.copyfileobj(r,f)
                if temp.stat().st_size<1_000_000:raise ValueError('Model tidak lengkap')
                temp.replace(model_path)
            except Exception:
                temp.unlink(missing_ok=True)
                raise RuntimeError('Unduhan model MediaPipe gagal. Jalankan scripts/download_model.py ketika online.')
        if not model_path.exists():raise RuntimeError('Model MediaPipe belum tersedia: '+str(model_path))
        import mediapipe as mp
        self.mp=mp
        self.detector=mp.tasks.vision.HandLandmarker.create_from_options(
            mp.tasks.vision.HandLandmarkerOptions(
                base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
                running_mode=mp.tasks.vision.RunningMode.VIDEO,num_hands=2,
                min_hand_detection_confidence=.55,min_hand_presence_confidence=.55,
                min_tracking_confidence=.5))
        self._last_ts=-1
    def detect(self,rgb):
        mp=self.mp
        ts=max(int(time.monotonic()*1000),self._last_ts+1)
        self._last_ts=ts
        image=mp.Image(image_format=mp.ImageFormat.SRGB,data=rgb)
        result=self.detector.detect_for_video(image,ts)
        hands=[]
        for i,points in enumerate(result.hand_landmarks):
            c=result.handedness[i][0] if i<len(result.handedness) and result.handedness[i] else None
            hands.append(HandObservation(tuple(Point(p.x,p.y,p.z) for p in points),
                        confidence=float(c.score) if c else .55,
                        handedness=str(c.category_name) if c else 'Unknown'))
        return hands
    def close(self):self.detector.close()
