"""Entry point aplikasi informasi cerdas FILKOM UB."""
import logging
import sys
from logging.handlers import RotatingFileHandler
from PySide6.QtWidgets import QApplication,QMessageBox
from config import ROOT, LOG_FILE
from app.services.content_repository import ContentError


def main():
    LOG_FILE.parent.mkdir(parents=True,exist_ok=True)
    logging.basicConfig(level=logging.INFO,handlers=[RotatingFileHandler(LOG_FILE,maxBytes=750000,backupCount=2,encoding='utf-8')],
                        format='%(asctime)s %(levelname)s %(name)s %(message)s')
    app=QApplication(sys.argv)
    app.setApplicationName('FILKOM UB - Layanan Informasi Cerdas')
    app.setStyle('Fusion')
    app.setStyleSheet((ROOT/'app'/'theme.qss').read_text(encoding='utf-8'))
    try:
        from app.main_window import MainWindow
        window=MainWindow()
    except (ContentError,OSError,ValueError) as e:
        QMessageBox.critical(None,'Data aplikasi tidak tersedia',str(e));return 2
    window.show()
    return app.exec()

if __name__=='__main__':raise SystemExit(main())
