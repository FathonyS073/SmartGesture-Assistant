from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage,QPixmap
from PySide6.QtWidgets import QFrame,QLabel,QSizePolicy
from app.widgets.graphics import vbox,hbox,panel,label,icon_label

class CameraWidget(QFrame):
    def __init__(self,parent=None):
        super().__init__(parent);self.setObjectName('CameraCard')
        root=vbox(self,8,(8,8,8,8))
        heading=panel('CameraHeading');hh=hbox(heading,10,(12,8,10,8))
        hh.addWidget(icon_label('camera',25));hh.addWidget(label('Deteksi Kamera','panelTitle'));hh.addStretch()
        root.addWidget(heading)
        self.display=label('Kamera belum aktif\nPilih perangkat kamera pada Pengaturan','cameraEmpty')
        self.display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display.setObjectName('CameraPreview')
        self.display.setMinimumHeight(190)
        self.display.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        root.addWidget(self.display,1)
        status=panel('CameraStatus');st=vbox(status,5,(9,8,9,8))
        row=hbox();row.addWidget(label('♧','blueGlyph',False));row.addWidget(label('Gestur terdeteksi:','smallBold',False))
        self.gesture=label('—','accent',False);row.addWidget(self.gesture);row.addStretch();st.addLayout(row)
        row2=hbox();row2.addWidget(label('⌁','blueGlyph',False));row2.addWidget(label('Status:','smallBold',False))
        self.state_label=label('Menunggu input','accent',False);row2.addWidget(self.state_label,1);st.addLayout(row2)
        self.debug=label('','meta');self.debug.setVisible(False);st.addWidget(self.debug)
        root.addWidget(status)
        self._last_image=None
    def set_frame(self,image:QImage):
        self._last_image=image;self._render_frame()
    def _render_frame(self):
        if self._last_image is None:return
        pix=QPixmap.fromImage(self._last_image)
        self.display.setPixmap(pix.scaled(self.display.size(),Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation))
    def resizeEvent(self,event):
        super().resizeEvent(event);self._render_frame()
    def set_gesture(self,gesture:str,hand_count:int):
        self.gesture.setText('—' if not hand_count else gesture.replace('THUMBS_UP','Thumbs Up').replace('FIST','Fist').replace('UNKNOWN','Tidak dikenali'))
    def set_state(self,state:str):self.state_label.setText(state)
    def set_debug(self,enabled:bool,fps:float=0.,latency:float=0.,confidence:float=0.):
        self.debug.setVisible(enabled)
        self.debug.setText(f'{fps:.1f} FPS · {latency:.0f} ms · Confidence {confidence:.2f}')
