from __future__ import annotations
from PySide6.QtCore import Signal,Qt
from PySide6.QtWidgets import QFrame,QLabel,QPushButton,QVBoxLayout,QHBoxLayout,QSizePolicy
from app.widgets.graphics import icon_label,label,ICON_NAMES,hbox,vbox
from app.models.menu import Menu

class MenuCard(QPushButton):
    selected=Signal(int)
    def __init__(self,menu:Menu,parent=None):
        super().__init__(parent)
        self.menu=menu;self.setObjectName('MenuCard');self.setProperty('selected','false')
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(76)
        layout=hbox(self,12,(12,7,12,7))
        self.num=QLabel(str(menu.id));self.num.setObjectName('MenuNumber')
        self.num.setFixedSize(39,39);self.num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.num)
        self.icon=icon_label(ICON_NAMES[menu.id-1],42)
        layout.addWidget(self.icon)
        text=vbox(spacing=3)
        self.title=label(menu.title,'menuTitle');self.subtitle=label(menu.subtitle,'menuSubtitle')
        text.addWidget(self.title);text.addWidget(self.subtitle)
        layout.addLayout(text,1)
        arr=label('›','arrow',False);layout.addWidget(arr)
        self.clicked.connect(lambda:self.selected.emit(self.menu.id))
    def mark(self,selected:bool,dim:bool=False):
        self.setProperty('selected','true' if selected else 'false')
        self.setProperty('dim','true' if dim and not selected else 'false')
        self.style().unpolish(self);self.style().polish(self)
