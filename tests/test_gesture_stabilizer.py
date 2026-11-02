from app.services.gesture_stabilizer import GestureStabilizer


def test_temporal_activation_and_hold_latched():
    s=GestureStabilizer(duration=.8,min_frames=4)
    t=0.;outputs=[]
    for i in range(32):
        x=s.feed('2',.96,t)
        if x:outputs.append(x)
        t+=.1
    assert outputs==['2']

def test_short_poses_and_low_confidence_do_not_fire():
    s=GestureStabilizer(duration=.8,min_frames=4)
    for i in range(8):assert s.feed('1',.94,i*.1) is None
    assert s.feed('1',.94,.81)=='1'
    for i in range(12):assert s.feed('THUMBS_UP',.4,1+i*.1) is None

def test_release_allows_repeating_same_pose():
    s=GestureStabilizer(duration=.5,min_frames=3)
    assert s.feed('FIST',.9,0) is None
    assert s.feed('FIST',.9,.25) is None
    assert s.feed('FIST',.9,.55)=='FIST'
    assert s.feed('FIST',.9,.65) is None
    assert s.feed('UNKNOWN',0,.8) is None
    assert s.feed('UNKNOWN',0,1.05) is None
    assert s.feed('FIST',.9,1.1) is None
    assert s.feed('FIST',.9,1.66) is None # only 2 frames
    assert s.feed('FIST',.9,1.75)=='FIST'

def test_changed_pose_can_rearm_without_oscillation():
    s=GestureStabilizer(duration=.4,min_frames=3)
    for t in (0,.2,.45):out=s.feed('2',.9,t)
    assert out=='2'
    for t in (.5,.6,.7,.8):assert s.feed('THUMBS_UP',.9,t) is None
    assert s.feed('THUMBS_UP',.9,.92)=='THUMBS_UP'
