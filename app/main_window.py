"""Three-state FILKOM UI, gestures and TTS integration."""
from __future__ import annotations
import logging
import time
from PySide6.QtCore import Qt,QTimer,QDateTime,Signal
from PySide6.QtGui import QFont,QIcon,QKeySequence,QShortcut
from PySide6.QtWidgets import (QMainWindow,QWidget,QFrame,QVBoxLayout,QHBoxLayout,
     QStackedWidget,QMessageBox,QDialog,QFormLayout,QDialogButtonBox,QComboBox,
     QSpinBox,QDoubleSpinBox,QCheckBox,QLabel,QPushButton,QSizePolicy)
from config import Settings,load_settings,save_settings,VOICES
from app.widgets.graphics import panel,label,hbox,vbox,tool_button,icon_label,icon_path
from app.widgets.camera_widget import CameraWidget
from app.widgets.gesture_footer import GestureFooter
from app.screens.home_screen import HomeScreen
from app.screens.confirmation_screen import ConfirmationScreen
from app.screens.detail_screen import DetailScreen
from app.services.content_repository import ContentRepository
from app.services.camera_worker import CameraWorker
from app.services.gesture_stabilizer import GestureStabilizer
from app.services.interaction_controller import InteractionController,State
from app.services.tts_service import TtsService
from app.services.audio_player import AudioPlayer
LOG=logging.getLogger(__name__)

class SettingsDialog(QDialog):
    def __init__(self,s:Settings,parent=None):
        super().__init__(parent);self.setWindowTitle('Pengaturan Aplikasi');self.setMinimumWidth(370)
        layout=QVBoxLayout(self);form=QFormLayout();layout.addLayout(form)
        self.cam=QSpinBox();self.cam.setRange(0,12);self.cam.setValue(s.camera_index)
        form.addRow('Indeks kamera',self.cam)
        self.stable=QDoubleSpinBox();self.stable.setRange(.3,3);self.stable.setSingleStep(.1)
        self.stable.setDecimals(1);self.stable.setSuffix(' detik');self.stable.setValue(s.stability_seconds)
        form.addRow('Durasi gestur stabil',self.stable)
        self.volume=QSpinBox();self.volume.setRange(0,100);self.volume.setSuffix(' %');self.volume.setValue(s.volume)
        form.addRow('Volume TTS',self.volume)
        self.voice=QComboBox();self.voice.addItems(VOICES);self.voice.setCurrentText(s.voice)
        form.addRow('Suara Bahasa Indonesia',self.voice)
        self.rate=QSpinBox();self.rate.setRange(-40,40);self.rate.setSuffix(' %');self.rate.setValue(s.speech_rate)
        form.addRow('Kecepatan suara',self.rate)
        self.mirror=QCheckBox('Cerminkan preview');self.mirror.setChecked(s.mirror_preview)
        self.overlay=QCheckBox('Tampilkan 21 landmark pada kamera');self.overlay.setChecked(s.show_landmarks)
        self.debug=QCheckBox('Tampilkan FPS, latensi, confidence');self.debug.setChecked(s.debug)
        for control in (self.mirror,self.overlay,self.debug):layout.addWidget(control)
        layout.addWidget(label('Perubahan indeks kamera akan me-restart tangkapan video.\nSuaranya memerlukan internet pada sintesis pertama.','meta'))
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Save|QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept);buttons.rejected.connect(self.reject);layout.addWidget(buttons)
    def apply(self,s:Settings)->None:
        s.camera_index=self.cam.value();s.stability_seconds=self.stable.value()
        s.volume=self.volume.value();s.voice=self.voice.currentText();s.speech_rate=self.rate.value()
        s.mirror_preview=self.mirror.isChecked();s.show_landmarks=self.overlay.isChecked()
        s.debug=self.debug.isChecked();s.validate()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings=load_settings()
        self.repository=ContentRepository()
        self.fsm=InteractionController()
        self.stabilizer=GestureStabilizer(self.settings.stability_seconds,
                       self.settings.min_frames,self.settings.min_confidence)
        self.audio_generation=0
        self.tts=TtsService(self)
        self.player=AudioPlayer(self.settings.volume,self)
        self.tts.ready.connect(self._on_audio_ready)
        self.tts.failed.connect(self._on_audio_failed)
        self.player.status.connect(self._on_audio_status)
        self.worker=None;self._pending_restart=False;self._is_closing=False
        self._camera_problem=''
        self.setWindowTitle('Layanan Informasi Cerdas — FILKOM UB')
        self.setWindowIcon(QIcon(icon_path('hand')))
        self.resize(1500,845);self.setMinimumSize(780,480)
        self._compact=None
        surface=QWidget();surface.setObjectName('Root');self.setCentralWidget(surface)
        body=vbox(surface,0)
        self._make_brand(body)
        self._make_masthead(body)
        center=panel('Body');lay=hbox(center,15,(18,20,18,12))
        self.camera=CameraWidget()
        self.camera.setMinimumWidth(260)
        lay.addWidget(self.camera,38)
        self.pages=QStackedWidget();self.pages.setMinimumWidth(450)
        self.home=HomeScreen(self.repository.menus)
        self.confirmation=ConfirmationScreen(self.repository.menus)
        self.detail=DetailScreen()
        for w in (self.home,self.confirmation,self.detail):self.pages.addWidget(w)
        lay.addWidget(self.pages,62)
        body.addWidget(center,1)
        self.footer=GestureFooter();body.addWidget(self.footer)
        self._update_responsive()
        self.home.selected.connect(self._choose_menu)
        self.confirmation.selected.connect(self._choose_menu)
        self.confirmation.confirm_requested.connect(lambda:self._perform('THUMBS_UP'))
        self.confirmation.cancel_requested.connect(lambda:self._perform('FIST'))
        self.detail.back_requested.connect(lambda:self._perform('FIST'))
        self.detail.replay_requested.connect(self._play_selected_narration)
        for n in range(1,11):
            QShortcut(QKeySequence(str(n%10)),self,activated=lambda k=n:self._perform(str(k)))
        QShortcut(QKeySequence('Return'),self,activated=lambda:self._perform('THUMBS_UP'))
        QShortcut(QKeySequence('Escape'),self,activated=lambda:self._perform('FIST'))
        self.clock_timer=QTimer(self);self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000);self._update_clock()
        QTimer.singleShot(150,self._start_camera)

    def _make_brand(self,parent):
        bar=panel('BrandBar');self.brand_bar=bar;bar.setFixedHeight(63)
        l=hbox(bar,12,(28,6,24,6))
        seal=label('◆','brandSeal',False);l.addWidget(seal)
        l.addWidget(label('UNIVERSITAS\nBRAWIJAYA','brandSmall',False))
        sep=QFrame();sep.setFrameShape(QFrame.Shape.VLine);sep.setObjectName('BrandSeparator');l.addWidget(sep)
        l.addWidget(label('◈ FILKOM UB','brandName',False))
        l.addWidget(label('Fakultas Ilmu Komputer','brandSub',False))
        l.addStretch()
        self.brand_caption=label('SISTEM INFORMASI CERDAS','brandCaption',False)
        l.addWidget(self.brand_caption)
        parent.addWidget(bar)

    def _make_masthead(self,parent):
        banner=panel('Masthead');self.masthead=banner;banner.setFixedHeight(131)
        row=hbox(banner,16,(26,17,26,14))
        appicon=panel('AppIcon');appicon.setFixedSize(90,80)
        box=vbox(appicon,0,(16,13,16,13));box.addWidget(icon_label('hand',54))
        self.masthead_app_icon=appicon
        row.addWidget(appicon)
        text=vbox(spacing=2)
        self.heading_label=label('Layanan Informasi Cerdas FILKOM UB','mainHeading')
        self.subtitle_label=label('Berbasis Pengenalan Gestur Tangan dan Text-to-Speech','subtitle')
        text.addWidget(self.heading_label)
        text.addWidget(self.subtitle_label)
        row.addLayout(text,1)
        status=panel('TopStatus');st=hbox(status,12,(10,8,10,8))
        self.cam_status=label('●  Kamera Memulai','cameraOff',False);st.addWidget(self.cam_status)
        st.addWidget(label('│','separator',False))
        self.clock=label('00:00:00','clock',False);st.addWidget(self.clock)
        row.addWidget(status)
        row.addWidget(tool_button('♙',self._show_about,'iconButton',44))
        row.addWidget(tool_button('?',self._show_help,'iconButton',44))
        row.addWidget(tool_button('⚙',self._show_settings,'iconButton',44))
        parent.addWidget(banner)


    def _update_responsive(self):
        if not hasattr(self,'footer'):return
        compact=self.width()<1120
        if compact==self._compact:return
        self._compact=compact
        self.brand_bar.setFixedHeight(47 if compact else 63)
        self.masthead.setFixedHeight(101 if compact else 131)
        self.brand_caption.setVisible(not compact)
        self.masthead_app_icon.setVisible(not compact)
        self.camera.display.setMinimumHeight(120 if compact else 190)
        self.footer.set_compact(compact)
        for widget in (self.heading_label,self.subtitle_label):
            widget.setProperty('compact','true' if compact else 'false')
            widget.style().unpolish(widget);widget.style().polish(widget)

    def resizeEvent(self,event):
        super().resizeEvent(event)
        self._update_responsive()

    def _update_clock(self):self.clock.setText(QDateTime.currentDateTime().toString('HH:mm:ss'))

    def _start_camera(self):
        if self._is_closing:return
        if self.worker and self.worker.isRunning():return
        self.cam_status.setText('●  Kamera Memulai')
        self._camera_problem=''
        self.worker=CameraWorker(self.settings.camera_index,self.settings.mirror_preview,
              self.settings.show_landmarks,self.settings.min_confidence,self)
        self.worker.image_ready.connect(self.camera.set_frame)
        self.worker.observation.connect(self._on_observation)
        self.worker.issue.connect(self._camera_issue)
        self.worker.running_changed.connect(self._camera_running)
        self.worker.finished.connect(self._camera_finished)
        self.worker.start()

    def _camera_finished(self):
        if self._pending_restart and not self._is_closing:
            self._pending_restart=False
            QTimer.singleShot(100,self._start_camera)

    def _camera_running(self,active:bool):
        self.cam_status.setText('●  Kamera Aktif' if active else '●  Kamera Tidak Aktif')
        self.cam_status.setProperty('status','on' if active else 'off')
        self.cam_status.style().unpolish(self.cam_status);self.cam_status.style().polish(self.cam_status)
        if not active and self.fsm.state==State.HOME:self.camera.set_state('Kamera tidak aktif')

    def _camera_issue(self,message:str):
        LOG.warning(message)
        self._camera_problem=message
        self.camera.set_state(message)

    def _on_observation(self,name:str,confidence:float,count:int,fps:float,latency:float):
        self.camera.set_gesture(name,count)
        self.camera.set_debug(self.settings.debug,fps,latency,confidence)
        if self._camera_problem:
            self.camera.set_state(self._camera_problem)
        elif count==0:
            if self.fsm.state==State.HOME:self.camera.set_state('Tidak ada tangan terdeteksi')
        elif self.fsm.state==State.HOME:self.camera.set_state('Menunggu pilihan menu')
        elif self.fsm.state==State.CONFIRMATION:self.camera.set_state('Menunggu konfirmasi')
        else:self.camera.set_state('Informasi aktif')
        triggered=self.stabilizer.feed(name,confidence,time.monotonic())
        if triggered:self._perform(triggered)

    def _choose_menu(self,number:int):
        # UI clicks are explicit individual actions, not fed back to temporal stabilizer.
        self._perform(str(number))

    def _perform(self,gesture:str):
        effects=self.fsm.dispatch(gesture)
        if not effects:return
        for effect in effects:
            if effect=='show_confirmation':
                n=self.fsm.selected
                self.confirmation.set_selection(n)
                self.pages.setCurrentWidget(self.confirmation)
                self.camera.set_state('Menunggu konfirmasi')
            elif effect=='show_detail':
                self.detail.set_menu(self.repository.get(self.fsm.selected))
                self.pages.setCurrentWidget(self.detail)
                self.camera.set_state('Informasi aktif')
            elif effect=='stop_audio':
                self.audio_generation+=1
                self.player.stop()
            elif effect=='show_home':
                self.pages.setCurrentWidget(self.home)
                self.camera.set_state('Menunggu input')
            elif effect=='play_audio':self._play_selected_narration()
        LOG.info('Gesture %s; current state %s; effects %s',gesture,self.fsm.state,effects)

    def _play_selected_narration(self):
        if self.fsm.state!=State.DETAIL or self.fsm.selected is None:return
        self.audio_generation+=1
        token=self.audio_generation
        self.player.stop()
        self.detail.set_audio_status('Menyiapkan narasi…')
        menu=self.repository.get(self.fsm.selected)
        self.tts.prepare(token,menu.narration_text,self.settings.voice,self.settings.speech_rate)

    def _on_audio_ready(self,token:int,path:str):
        if token!=self.audio_generation or self.fsm.state!=State.DETAIL:return
        self.player.play_file(path)
    def _on_audio_failed(self,token:int,message:str):
        if token==self.audio_generation and self.fsm.state==State.DETAIL:
            self.detail.set_audio_status(message)
    def _on_audio_status(self,status:str):
        if self.fsm.state==State.DETAIL:self.detail.set_audio_status(status)

    def _show_settings(self):
        dialog=SettingsDialog(self.settings,self)
        if dialog.exec()!=QDialog.DialogCode.Accepted:return
        old_camera=self.settings.camera_index
        dialog.apply(self.settings);save_settings(self.settings)
        self.player.set_volume(self.settings.volume)
        self.stabilizer.duration=self.settings.stability_seconds
        self.stabilizer.min_confidence=self.settings.min_confidence
        self.stabilizer.reset()
        if self.worker:
            if not self.worker.isRunning():
                self._start_camera()
            elif self.settings.camera_index!=old_camera:
                if self.worker.isRunning():
                    self._pending_restart=True;self.worker.stop()
                else:self._start_camera()
            else:
                self.worker.mirror=self.settings.mirror_preview
                self.worker.overlay=self.settings.show_landmarks
                self.worker.min_confidence=self.settings.min_confidence
        else:self._start_camera()

    def _show_help(self):
        QMessageBox.information(self,'Petunjuk Gestur',
            'ANGKA 1–5: satu tangan dengan telunjuk, lalu tambah jari berurutan.\n'
            'ANGKA 6–10: satu tangan menunjukkan lima jari, tangan kedua 1–5 jari.\n'
            'THUMBS UP: ibu jari menunjuk atas, empat jari lain menutup.\n'
            'FIST: mengepal untuk membatalkan atau kembali.\n\n'
            'Tahan gestur hingga stabil ±0,8 detik (dapat diatur). Lepaskan sebelum mengulang.\n'
            'Akses alternatif: klik menu, tekan Enter untuk konfirmasi, Esc untuk kembali.\n'
            'Tombol angka keyboard 1–9 dan 0 (menu 10) dapat dipakai untuk debugging.')
    def _show_about(self):
        QMessageBox.information(self,'Tentang Aplikasi',
           'Layanan Informasi Cerdas FILKOM UB — prototipe penelitian.\n'
           'Tidak mengumpulkan atau menyimpan citra webcam.\n'
           'Konten dari dokumen Rancangan 1.0, 2 November 2026.\n'
           'Belum merupakan materi resmi yang disahkan FILKOM UB.')
    def closeEvent(self,event):
        self._is_closing=True
        self.audio_generation+=1;self.player.stop()
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            if not self.worker.wait(3000):
                self._is_closing=False
                QMessageBox.warning(self,'Kamera','Kamera masih menutup. Coba tutup kembali setelah proses selesai.')
                event.ignore();return
        super().closeEvent(event)
