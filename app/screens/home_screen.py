from __future__ import annotations
from PySide6.QtCore import Signal,Qt
from PySide6.QtWidgets import QWidget,QFrame,QGridLayout,QScrollArea,QVBoxLayout
from app.widgets.graphics import vbox,hbox,label,panel
from app.widgets.menu_card import MenuCard
from app.models.menu import Menu

class HomeScreen(QWidget):
    selected=Signal(int)
    def __init__(self,menus:dict[int,Menu],parent=None):
        super().__init__(parent)
        root=vbox(self,12,(4,4,4,4))
        banner=panel('InfoBanner');hb=hbox(banner,10,(16,9,12,9))
        hb.addWidget(label('ⓘ','infoIcon',False));hb.addWidget(label('Silakan pilih menu menggunakan gestur tangan','bannerTitle'))
        root.addWidget(banner)
        scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content=QWidget();grid=QGridLayout(content);grid.setContentsMargins(0,4,1,5);grid.setSpacing(12)
        self.cards={}
        for i,menu in menus.items():
            card=MenuCard(menu);card.selected.connect(self.selected.emit)
            grid.addWidget(card,(i-1)//2,(i-1)%2)
            self.cards[i]=card
        grid.setColumnStretch(0,1);grid.setColumnStretch(1,1)
        scroll.setWidget(content)
        root.addWidget(scroll,1)
