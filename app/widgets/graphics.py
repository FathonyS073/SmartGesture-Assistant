"""Reusable widget constructors; Qt-native images rendered from local SVG icons."""
from __future__ import annotations
from pathlib import Path
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (QFrame,QLabel,QPushButton,QVBoxLayout,QHBoxLayout,QWidget,
                               QGraphicsDropShadowEffect)
from PySide6.QtGui import QColor,QPixmap,QIcon,QPainter
from PySide6.QtSvg import QSvgRenderer
from config import ROOT

ICON_NAMES=['landmark','building','graduation','monitor','file','users','award','people','microscope','map-pin']

def icon_path(name:str)->str:return str(ROOT/'assets'/'icons'/(name+'.svg'))

def icon_pixmap(name:str,size:int=48)->QPixmap:
    pix=QPixmap(size,size)
    pix.fill(Qt.GlobalColor.transparent)
    painter=QPainter(pix)
    QSvgRenderer(icon_path(name)).render(painter)
    painter.end()
    return pix

def icon_label(name:str,size:int=40)->QLabel:
    label=QLabel()
    pix=icon_pixmap(name,size)
    label.setPixmap(pix.scaled(size,size,Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation))
    label.setFixedSize(size,size)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return label

def label(text:str='',role:str='',wrap:bool=True)->QLabel:
    l=QLabel(text)
    l.setWordWrap(wrap)
    if role:l.setProperty('role',role)
    return l

def panel(name:str='Card')->QFrame:
    f=QFrame();f.setObjectName(name)
    return f

def shadow(widget:QWidget,blur:int=18,alpha:int=32):
    effect=QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur);effect.setOffset(0,4);effect.setColor(QColor(19,62,125,alpha))
    widget.setGraphicsEffect(effect)

def hbox(parent=None,spacing:int=10,margins=(0,0,0,0)):
    lay=QHBoxLayout(parent);lay.setContentsMargins(*margins);lay.setSpacing(spacing)
    return lay

def vbox(parent=None,spacing:int=10,margins=(0,0,0,0)):
    lay=QVBoxLayout(parent);lay.setContentsMargins(*margins);lay.setSpacing(spacing)
    return lay

def tool_button(text:str,action,kind:str='light',height:int=36)->QPushButton:
    b=QPushButton(text);b.setObjectName(kind);b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.setMinimumHeight(height);b.clicked.connect(action)
    return b
