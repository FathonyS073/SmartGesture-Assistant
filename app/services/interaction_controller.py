"""UI-independent finite state machine; emits pure effect names for testability."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class State(str,Enum):
    HOME='HOME';CONFIRMATION='CONFIRMATION';DETAIL='DETAIL'

@dataclass
class InteractionController:
    state:State=State.HOME
    selected:int|None=None
    def dispatch(self,gesture:str)->tuple[str,...]:
        if self.state==State.HOME:
            if gesture.isdigit() and 1<=int(gesture)<=10:
                self.selected=int(gesture);self.state=State.CONFIRMATION
                return ('show_confirmation',)
        elif self.state==State.CONFIRMATION:
            if gesture=='FIST':
                self.selected=None;self.state=State.HOME
                return ('show_home',)
            if gesture.isdigit() and 1<=int(gesture)<=10:
                self.selected=int(gesture)
                return ('show_confirmation',)
            if gesture=='THUMBS_UP' and self.selected is not None:
                self.state=State.DETAIL
                return ('show_detail','play_audio')
        elif self.state==State.DETAIL and gesture=='FIST':
            self.selected=None;self.state=State.HOME
            return ('stop_audio','show_home')
        return ()
