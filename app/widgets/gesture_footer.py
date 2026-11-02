from __future__ import annotations
from PySide6.QtWidgets import QFrame,QSizePolicy
from app.widgets.graphics import hbox,label

class GestureFooter(QFrame):
    def __init__(self,parent=None):
        super().__init__(parent);self.setObjectName('Footer')
        lay=hbox(self,12,(14,10,14,10))
        self.labels=[]
        for text,role in [('♧  Petunjuk Gestur','footerTitle'),('♧  Angka 1–10: Pilih menu','footerBlue'),
                          ('👍  Thumbs Up: Konfirmasi','footerGreen'),('✊  Fist: Kembali','footerRed')]:
            badge=QFrame();badge.setObjectName(role)
            line=hbox(badge,8,(12,7,12,7))
            lbl=label(text,role,False);line.addWidget(lbl)
            self.labels.append(lbl)
            lay.addWidget(badge,1)

    def set_compact(self,compact:bool):
        texts=(('♧  Gestur','1–10: Pilih','👍: YA','✊: Kembali') if compact else
               ('♧  Petunjuk Gestur','♧  Angka 1–10: Pilih menu','👍  Thumbs Up: Konfirmasi','✊  Fist: Kembali'))
        for label,text in zip(self.labels,texts):label.setText(text)
