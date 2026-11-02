from app.services.gesture_classifier import classify_hands,finger_states,Gesture,UNKNOWN
from synthetic_hands import hand


def test_single_hand_numbers_both_handedness():
    for side in ('Left','Right'):
        for n in range(1,6):
            actual=classify_hands([hand(n,handedness=side)])
            assert actual.label==str(n),(n,side,actual,finger_states(hand(n).points))

def test_two_hands_6_to_10_order_irrelevant():
    for n in range(1,6):
        assert classify_hands([hand(5),hand(n,handedness='Right')]).label==str(n+5)
        assert classify_hands([hand(n,handedness='Right'),hand(5)]).label==str(n+5)

def test_thumb_vs_index_and_fist():
    assert classify_hands([hand(1)]).label=='1'
    assert classify_hands([hand(0,thumb_up=True)]).label=='THUMBS_UP'
    assert classify_hands([hand(0)]).label=='FIST'

def test_ambiguous_two_hands_not_fist_or_number():
    for a,b in ((0,0),(5,0),(4,4),(1,1),(5,1)):
        result=classify_hands([hand(a),hand(b)])
        if (a,b)==(5,1):assert result.label=='6'
        else:assert result.label=='UNKNOWN'

def test_confidence_invalid_landmarks():
    assert classify_hands([hand(1,confidence=.4)]).label=='UNKNOWN'
    assert classify_hands([hand(5)]*3).label=='UNKNOWN'
