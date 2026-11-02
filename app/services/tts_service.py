"""Neural Indonesian synthesis off Qt GUI thread with content-addressed disk cache."""
from __future__ import annotations
import asyncio
import hashlib
import logging
import os
from pathlib import Path
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from config import CACHE_DIR
LOG=logging.getLogger(__name__)

class TtsJobSignals(QObject):
    done=Signal(int,str)
    error=Signal(int,str)

class TtsJob(QRunnable):
    def __init__(self,token:int,text:str,voice:str,rate:int,path:Path):
        super().__init__();self.token=token;self.text=text;self.voice=voice;self.rate=rate;self.path=path
        self.signals=TtsJobSignals()
    def run(self):
        tmp=self.path.with_name(self.path.stem+f'-{self.token}.tmp.mp3')
        try:
            self.path.parent.mkdir(exist_ok=True,parents=True)
            if not self.path.is_file() or self.path.stat().st_size<1024:
                import edge_tts
                async def produce():
                    client=edge_tts.Communicate(self.text,self.voice,rate=f'{self.rate:+d}%')
                    await client.save(str(tmp))
                asyncio.run(produce())
                if not tmp.exists() or tmp.stat().st_size<1024:
                    raise RuntimeError('Data audio yang dihasilkan tidak lengkap.')
                os.replace(tmp,self.path)
            self.signals.done.emit(self.token,str(self.path))
        except Exception as exc:
            LOG.exception('Sintesis TTS gagal')
            if self.path.exists() and self.path.stat().st_size>=1024:
                self.signals.done.emit(self.token,str(self.path))
            else:
                self.signals.error.emit(self.token,'Audio tidak tersedia. Periksa internet atau cache lokal. '+str(exc))
        finally:tmp.unlink(missing_ok=True)

class TtsService(QObject):
    ready=Signal(int,str)
    failed=Signal(int,str)
    def __init__(self,parent=None):
        super().__init__(parent);self.pool=QThreadPool.globalInstance();self._jobs=[]
    def prepare(self,token:int,text:str,voice:str,rate:int)->None:
        digest=hashlib.sha256((voice+'\0'+str(rate)+'\0'+text).encode('utf-8')).hexdigest()
        path=CACHE_DIR/(digest+'.mp3')
        if path.exists() and path.stat().st_size>=1024:
            self.ready.emit(token,str(path));return
        job=TtsJob(token,text,voice,rate,path)
        job.signals.done.connect(self.ready.emit)
        job.signals.error.connect(self.failed.emit)
        self._jobs.append(job)
        # Hold signal sources until the pool has emitted completion; don't reuse filenames.
        def cleanup(_token,*_):
            if job in self._jobs:self._jobs.remove(job)
        job.signals.done.connect(cleanup)
        job.signals.error.connect(cleanup)
        self.pool.start(job)
