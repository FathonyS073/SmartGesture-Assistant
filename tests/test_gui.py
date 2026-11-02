"""Optional Qt smoke test (requires PySide6 installed and an available Qt platform plugin)."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import pytest
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from app.main_window import MainWindow
from app.services.interaction_controller import State


def test_gui_navigation(monkeypatch):
    monkeypatch.setattr(MainWindow,'_start_camera',lambda self:None)
    app=QApplication.instance() or QApplication([])
    window=MainWindow()
    for w,h in ((1366,768),(1600,900),(1672,941),(1920,1080)):
        window.resize(w,h);window.show();app.processEvents()
        assert window.pages.width()>500
        assert window.camera.width()>300
    window._perform('2')
    assert window.fsm.state==State.CONFIRMATION
    assert window.confirmation.menu_title.text()=='Fasilitas'
    # Prevent real TTS in GUI smoke tests.
    monkeypatch.setattr(window,'_play_selected_narration',lambda:None)
    window._perform('THUMBS_UP')
    assert window.fsm.state==State.DETAIL
    assert 'Fasilitas' in window.detail.title.text()
    window._perform('FIST')
    assert window.fsm.state==State.HOME
    window.close()
