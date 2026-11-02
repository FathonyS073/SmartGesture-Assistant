from __future__ import annotations
from PySide6.QtCore import Qt,Signal
from PySide6.QtWidgets import QWidget,QFrame,QGridLayout,QScrollArea
from app.widgets.graphics import hbox,vbox,label,panel,tool_button,icon_label,icon_pixmap,ICON_NAMES,shadow
from app.widgets.menu_card import MenuCard
from app.models.menu import Menu

class ConfirmationScreen(QWidget):
    selected=Signal(int)
    confirm_requested=Signal()
    cancel_requested=Signal()
    def __init__(self,menus:dict[int,Menu],parent=None):
        super().__init__(parent);self.menus=menus
        root=vbox(self,12,(4,4,4,4))
        banner=panel('InfoBanner');hb=hbox(banner,10,(16,9,12,9))
        hb.addWidget(label('ⓘ','infoIcon',False));hb.addWidget(label('Konfirmasi pilihan menu yang Anda inginkan','bannerTitle'))
        root.addWidget(banner)
        grid_holder=QWidget();base=vbox(grid_holder,0)
        scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        content=QWidget();grid=QGridLayout(content);grid.setSpacing(12);grid.setContentsMargins(0,4,0,4)
        self.cards={}
        for number,menu in menus.items():
            card=MenuCard(menu);card.selected.connect(self.selected.emit)
            grid.addWidget(card,(number-1)//2,(number-1)%2)
            self.cards[number]=card
        grid.setColumnStretch(0,1);grid.setColumnStretch(1,1)
        scroll.setWidget(content);base.addWidget(scroll)
        root.addWidget(grid_holder,1)
        self.overlay=panel('ConfirmModal');self.overlay.setParent(grid_holder)
        shadow(self.overlay,29,75)
        lay=vbox(self.overlay,10,(18,14,18,14))
        self.picture=icon_label('building',62);lay.addWidget(self.picture,0,Qt.AlignmentFlag.AlignHCenter)
        title=label('Konfirmasi Pilihan','confirmTitle');title.setAlignment(Qt.AlignmentFlag.AlignCenter);lay.addWidget(title)
        self.menu_title=label('','chosenTitle');self.menu_title.setAlignment(Qt.AlignmentFlag.AlignCenter);lay.addWidget(self.menu_title)
        question=label('Anda memilih menu ini.\nTampilkan informasi dan putar narasi suara?','confirmQuestion')
        question.setAlignment(Qt.AlignmentFlag.AlignCenter);lay.addWidget(question)
        yes=tool_button('👍  Thumbs Up untuk YA',self.confirm_requested.emit,'greenAction',43)
        no=tool_button('✊  Fist untuk BATAL / KEMBALI',self.cancel_requested.emit,'redAction',43)
        lay.addWidget(yes);lay.addWidget(no)
        lay.addWidget(label('ⓘ  Informasi dibuka setelah konfirmasi gestur terdeteksi stabil.','confirmNote'))
        self.overlay.setFixedWidth(365)
        self.overlay.adjustSize()
        self.overlay.raise_()
        self._holder=grid_holder
    def set_selection(self,number:int):
        for n,card in self.cards.items():card.mark(n==number,True)
        self.menu_title.setText(self.menus[number].title)
        self.picture.setPixmap(icon_pixmap(ICON_NAMES[number-1],62))
        self._position()
    def _position(self):
        self.overlay.adjustSize()
        self.overlay.move(max(0,(self._holder.width()-self.overlay.width())//2),
                          max(0,(self._holder.height()-self.overlay.height())//2))
        self.overlay.raise_()
    def resizeEvent(self,event):
        super().resizeEvent(event);self._position()
