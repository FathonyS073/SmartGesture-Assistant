"""Check audio effects with a fake backend: no speaker or network used."""
from app.services.gesture_stabilizer import GestureStabilizer
from app.services.interaction_controller import InteractionController,State

class FakeAudio:
    def __init__(self):self.played=[];self.stops=0
    def play(self,menu):self.played.append(menu)
    def stop(self):self.stops+=1

def drive(controller,audio,gesture):
    for action in controller.dispatch(gesture):
        if action=='play_audio':audio.play(controller.selected)
        if action=='stop_audio':audio.stop()

def test_one_speech_per_confirmation_revisit_and_stop():
    c=InteractionController();a=FakeAudio()
    drive(c,a,'2')
    assert a.played==[]
    drive(c,a,'THUMBS_UP')
    assert a.played==[2]
    for _ in range(40):drive(c,a,'THUMBS_UP')
    assert a.played==[2]
    drive(c,a,'FIST')
    assert a.stops==1
    drive(c,a,'2');drive(c,a,'THUMBS_UP')
    assert a.played==[2,2]
    drive(c,a,'FIST')
    assert a.stops==2

def test_stabilizer_held_fist_stops_once():
    c=InteractionController();a=FakeAudio()
    drive(c,a,'2');drive(c,a,'THUMBS_UP')
    stabilizer=GestureStabilizer(.8,4)
    for i in range(32):
        gesture=stabilizer.feed('FIST',.97,i*.1)
        if gesture:drive(c,a,gesture)
    assert a.stops==1 and c.state==State.HOME
