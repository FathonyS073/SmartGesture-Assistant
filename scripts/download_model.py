"""Unduh model HandLandmarker resmi satu kali (memerlukan internet)."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.services.hand_landmarker import LandmarkEngine
from config import MODEL_FILE

if __name__=='__main__':
    print('Mengunduh/membuka model:',MODEL_FILE)
    engine=LandmarkEngine()
    engine.close()
    print('Model siap:',MODEL_FILE.stat().st_size,'byte')
