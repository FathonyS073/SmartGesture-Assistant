"""Artificial 21-point hands. Only exercises deterministic geometry, not CV accuracy."""
from app.services.gesture_classifier import Point,HandObservation

def hand(n:int=0,thumb_up:bool=False,handedness:str='Left',confidence:float=.94)->HandObservation:
    # n = canonical 1..5; n=0 fist; thumb_up is 11th gesture.
    p=[Point(.50,.93) for _ in range(21)]
    p[0]=Point(.50,.93)
    if n==5 or thumb_up:
        t=[(.36,.76),(.33,.62),(.30,.48),(.27,.25)] if thumb_up else [(.39,.75),(.30,.61),(.22,.47),(.10,.34)]
    else:t=[(.42,.75),(.39,.69),(.44,.74),(.46,.80)]
    for idx,xy in zip((1,2,3,4),t):p[idx]=Point(*xy)
    x_positions=(.41,.50,.59,.68)
    for finger,x in enumerate(x_positions):
        base=5+finger*4
        is_extended=(n==5 or (n>0 and finger<n)) and not thumb_up
        coords= [(x,.56),(x,.43),(x,.30),(x,.16)] if is_extended else [(x,.56),(x,.43),(x+.02,.57),(x+.03,.74)]
        for idx,xy in enumerate(coords):p[base+idx]=Point(*xy)
    return HandObservation(tuple(p),confidence,handedness)
