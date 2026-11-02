from __future__ import annotations
from html import escape
from PySide6.QtCore import Qt,Signal,QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QWidget,QFrame,QScrollArea,QSizePolicy
from app.widgets.graphics import vbox,hbox,panel,label,icon_label,icon_pixmap,ICON_NAMES,tool_button
from app.models.menu import Menu

class DetailScreen(QWidget):
    back_requested=Signal()
    replay_requested=Signal()
    def __init__(self,parent=None):
        super().__init__(parent)
        self.root=vbox(self,10,(4,4,4,4))
        self.top=panel('DetailHeading');row=hbox(self.top,12,(10,6,10,6))
        self.icon_box=icon_label('landmark',48);row.addWidget(self.icon_box)
        self.title=label('','detailTitle');row.addWidget(self.title,1)
        self.audio=label('Audio belum diputar','audioBadge');row.addWidget(self.audio)
        self.root.addWidget(self.top)
        self.intro=label('','introText');self.intro.setObjectName('Intro')
        self.intro.setContentsMargins(14,10,14,10)
        self.root.addWidget(self.intro)
        self.content_area=QWidget();self.columns=hbox(self.content_area,14,(0,5,0,5))
        self.scroll=QScrollArea();self.scroll.setWidgetResizable(True);self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.items_container=QWidget();self.items=vbox(self.items_container,10,(1,1,1,1))
        self.scroll.setWidget(self.items_container)
        self.columns.addWidget(self.scroll,7)
        self.summary=panel('SummaryCard');self.summary.setMinimumWidth(205)
        self.s_layout=vbox(self.summary,13,(14,14,14,14))
        self.s_title=label('ⓘ  Ringkasan','summaryTitle');self.s_layout.addWidget(self.s_title)
        self.s_body=label('','summaryText');self.s_layout.addWidget(self.s_body)
        self.note=label('','noteText');self.s_layout.addWidget(self.note)
        self.source_title=label('Sumber rujukan resmi','sourceHeading');self.s_layout.addWidget(self.source_title)
        self.source_controls=vbox(spacing=5);self.s_layout.addLayout(self.source_controls)
        self.s_layout.addStretch()
        self.columns.addWidget(self.summary,3)
        self.root.addWidget(self.content_area,1)
        self.controls=hbox(spacing=8)
        self.controls.addWidget(tool_button('←  Kembali (Fist)',self.back_requested.emit,'light',34))
        self.controls.addStretch()
        self.controls.addWidget(tool_button('▶  Putar ulang narasi',self.replay_requested.emit,'light',34))
        self.root.addLayout(self.controls)
    def set_menu(self,menu:Menu):
        self.title.setText(menu.title+' FILKOM')
        self.icon_box.setPixmap(icon_pixmap(ICON_NAMES[menu.id-1],48))
        self.intro.setText(menu.intro)
        while self.items.count():
            child=self.items.takeAt(0)
            if child.widget():child.widget().deleteLater()
        for idx,section in enumerate(menu.sections):
            card=panel('SectionCard');r=hbox(card,12,(12,10,12,10))
            r.addWidget(icon_label(ICON_NAMES[menu.id-1],50))
            text=vbox(spacing=5)
            text.addWidget(label(section.title,'sectionTitle'))
            text.addWidget(label(section.body,'sectionBody'))
            r.addLayout(text,1)
            self.items.addWidget(card)
        self.items.addStretch()
        self.s_body.setText('•  '+menu.summary)
        self.note.setText('DRAF PENELITIAN — belum disahkan FILKOM UB.\n'+menu.validation_note +
            ('\n\nPeriksa informasi terbaru pada situs resmi.' if menu.requires_current_information_check else ''))
        while self.source_controls.count():
            item=self.source_controls.takeAt(0)
            if item.widget():item.widget().deleteLater()
        for idx,url in enumerate(menu.source_urls,1):
            b=tool_button(f'↗  Sumber resmi {idx}',lambda checked=False,u=url:QDesktopServices.openUrl(QUrl(u)),'sourceButton',28)
            b.setToolTip(url)
            self.source_controls.addWidget(b)
        self.scroll.verticalScrollBar().setValue(0)
        self.audio.setText('Menyiapkan narasi…')
    def set_audio_status(self,status:str):self.audio.setText('🔊  '+status)
