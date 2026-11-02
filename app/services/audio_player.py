"""Actual Qt multimedia state rather than optimistic UI audio status."""
from __future__ import annotations
from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer

class AudioPlayer(QObject):
    status=Signal(str)
    def __init__(self,volume:int=80,parent=None):
        super().__init__(parent)
        self.output=QAudioOutput(self)
        self.player=QMediaPlayer(self)
        self.player.setAudioOutput(self.output)
        self.set_volume(volume)
        self.player.playbackStateChanged.connect(self._playback_state)
        self.player.mediaStatusChanged.connect(self._media_status)
        self.player.errorOccurred.connect(self._error)
        self._cancelled=False
    def set_volume(self,value:int):self.output.setVolume(max(0,min(100,value))/100)
    def play_file(self,path:str)->None:
        self._cancelled=False
        self.player.stop()
        self.player.setSource(QUrl.fromLocalFile(path))
        self.status.emit('Memuat audio…')
        self.player.play()
    def stop(self)->None:
        self._cancelled=True
        self.player.stop()
        self.player.setSource(QUrl())
        self.status.emit('Narasi dihentikan')
    def _playback_state(self,state):
        if state==QMediaPlayer.PlaybackState.PlayingState:self.status.emit('Narasi suara sedang diputar')
    def _media_status(self,state):
        if state==QMediaPlayer.MediaStatus.EndOfMedia and not self._cancelled:
            self.status.emit('Narasi selesai')
        elif state==QMediaPlayer.MediaStatus.InvalidMedia and not self._cancelled:
            self.status.emit('Audio tidak tersedia: format tidak didukung')
    def _error(self,_error,message):
        if not self._cancelled:self.status.emit('Audio tidak tersedia: '+message)
