"""Optional screenshots from live-created Qt widgets (no webcam or audio required)."""
import os
import sys
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from PySide6.QtWidgets import QApplication
from app.main_window import MainWindow

if __name__=='__main__':
    MainWindow._start_camera=lambda self:None
    app=QApplication([])
    app.setStyle('Fusion')
    app.setStyleSheet((ROOT/'app'/'theme.qss').read_text(encoding='utf-8'))
    win=MainWindow();win.resize(1672,941);win.show();app.processEvents()
    folder=ROOT/'screenshots';folder.mkdir(exist_ok=True)
    win.grab().save(str(folder/'01_home_qt.png'))
    win._perform('2');app.processEvents();win.grab().save(str(folder/'02_confirmation_qt.png'))
    # Avoid triggering network/audio in screenshot script.
    win._play_selected_narration=lambda:None
    win._perform('THUMBS_UP');app.processEvents();win.grab().save(str(folder/'03_detail_qt.png'))
    win.close()
    print('Screenshot actual Qt windows saved to',folder)
