"""Webcam + CV on QThread; no GUI access from camera thread."""
from __future__ import annotations
import logging
import sys
import time
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage
from app.services.gesture_classifier import classify_hands
from app.services.hand_landmarker import LandmarkEngine
LOG=logging.getLogger(__name__)
CONNECTIONS=[(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),
             (5,9),(9,10),(10,11),(11,12),(9,13),(13,14),(14,15),(15,16),
             (0,17),(17,18),(18,19),(19,20),(5,9),(9,13),(13,17)]

class CameraWorker(QThread):
    image_ready=Signal(QImage)
    observation=Signal(str,float,int,float,float) # gesture, confidence, hand_count, fps, latency_ms
    issue=Signal(str)
    running_changed=Signal(bool)
    def __init__(self,camera_index:int=0,mirror:bool=True,overlay:bool=False,min_confidence:float=.55,parent=None):
        super().__init__(parent)
        self.camera_index=camera_index
        self.mirror=mirror;self.overlay=overlay;self.min_confidence=min_confidence
        self._active=True

    def stop(self):self._active=False

    def run(self):
        import cv2
        import numpy as np
        api=cv2.CAP_DSHOW if sys.platform=='win32' else cv2.CAP_ANY
        capture=cv2.VideoCapture(self.camera_index,api)
        if not capture.isOpened():
            self.issue.emit('Kamera tidak ditemukan. Pilih perangkat lain di Pengaturan.')
            self.running_changed.emit(False)
            capture.release();return
        capture.set(cv2.CAP_PROP_FRAME_WIDTH,960)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT,540)
        capture.set(cv2.CAP_PROP_BUFFERSIZE,1)
        engine=None
        try:engine=LandmarkEngine()
        except Exception as e:
            LOG.exception('MediaPipe tidak siap')
            self.issue.emit('Deteksi gestur tidak tersedia: '+str(e))
        self.running_changed.emit(True)
        recent=time.monotonic()
        try:
            failures=0
            while self._active:
                ok,bgr=capture.read()
                if not ok:
                    failures+=1
                    if failures>15:
                        self.issue.emit('Kamera terputus atau gagal membaca frame.')
                        break
                    self.msleep(60);continue
                failures=0
                start=time.monotonic()
                # Inference on original (unmirrored) pixels.
                rgb=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
                hands=[]
                if engine:
                    try:hands=engine.detect(np.ascontiguousarray(rgb))
                    except Exception as e:
                        self.issue.emit('Kesalahan MediaPipe: '+str(e))
                        engine.close();engine=None
                gesture=classify_hands(hands,self.min_confidence)
                if self.overlay:
                    h,w=rgb.shape[:2]
                    for hand in hands:
                        for a,b in CONNECTIONS:
                            p=hand.points[a];q=hand.points[b]
                            cv2.line(rgb,(int(p.x*w),int(p.y*h)),(int(q.x*w),int(q.y*h)),(69,205,255),2)
                        for p in hand.points:
                            cv2.circle(rgb,(int(p.x*w),int(p.y*h)),4,(255,255,255),-1)
                if self.mirror:rgb=cv2.flip(rgb,1)
                rgb=np.ascontiguousarray(rgb)
                h,w=rgb.shape[:2]
                qimage=QImage(rgb.data,w,h,w*3,QImage.Format.Format_RGB888).copy()
                now=time.monotonic();dt=max(now-recent,.001);recent=now
                self.image_ready.emit(qimage)
                self.observation.emit(gesture.label,gesture.confidence,len(hands),min(1/dt,99), (now-start)*1000)
                self.msleep(10)
        finally:
            if engine:engine.close()
            capture.release()
            self.running_changed.emit(False)
