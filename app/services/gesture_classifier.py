"""Deterministic 21-point hand-landmark gesture classifier.

Input is image-normalized landmarks, independent of left/right-handed label.
Designed for front-facing upright hands, with moderate rotation tolerance.
No trained gesture recognizer is implied; requires real-camera accuracy study.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import acos, degrees, hypot
from typing import Sequence

@dataclass(frozen=True)
class Point:
    x:float
    y:float
    z:float=0.0

@dataclass(frozen=True)
class HandObservation:
    points:tuple[Point,...]
    confidence:float=1.0
    handedness:str='Unknown'

@dataclass(frozen=True)
class Gesture:
    label:str
    confidence:float
    fingers:tuple[bool,...]=()

UNKNOWN=Gesture('UNKNOWN',0.0)
# Finger order: thumb, index, middle, ring, little.
FINGER_IDS=((1,2,3,4),(5,6,7,8),(9,10,11,12),(13,14,15,16),(17,18,19,20))

def _dist(a:Point,b:Point)->float:return hypot(a.x-b.x,a.y-b.y)

def _angle(a:Point,b:Point,c:Point)->float:
    ax=a.x-b.x;ay=a.y-b.y;cx=c.x-b.x;cy=c.y-b.y
    size=hypot(ax,ay)*hypot(cx,cy)
    if size<1e-7:return 0.
    cos=max(-1.,min(1.,(ax*cx+ay*cy)/size))
    return degrees(acos(cos))

def finger_states(points:Sequence[Point])->tuple[bool,...]:
    if len(points)!=21:raise ValueError('Satu tangan harus memiliki 21 landmark.')
    palm=max(_dist(points[0],points[9]),1e-5)
    # Thumb: IP and MCP unfolded with the tip clearly away from index MCP.
    thumb=(_angle(points[2],points[3],points[4])>152 and
           _angle(points[1],points[2],points[4])>143 and
           _dist(points[4],points[5]) > .65*palm and
           _dist(points[4],points[9]) > .73*palm)
    states=[thumb]
    for mcp,pip,dip,tip in FINGER_IDS[1:]:
        straight=_angle(points[mcp],points[pip],points[dip])>153 and _angle(points[pip],points[dip],points[tip])>150
        reach=_dist(points[tip],points[0]) > _dist(points[pip],points[0])*1.16
        states.append(straight and reach)
    return tuple(states)

def _is_thumbs_up(p:Sequence[Point],bits:tuple[bool,...])->bool:
    if bits!=(True,False,False,False,False):return False
    # Thumb must point screen-up, away from the wrist. Not simply "one finger".
    tip=p[4];joint=p[2]
    return (joint.y-tip.y > .33*_dist(p[0],p[9]) and
            abs(tip.x-joint.x) < (joint.y-tip.y)*.9 and
            _dist(p[4],p[0]) > _dist(p[2],p[0]))

def classify_hands(hands:Sequence[HandObservation],min_confidence:float=.55)->Gesture:
    if not hands or len(hands)>2:return UNKNOWN
    if any(len(h.points)!=21 or h.confidence<min_confidence for h in hands):return UNKNOWN
    bits=[finger_states(h.points) for h in hands]
    conf=min(h.confidence for h in hands)
    if len(hands)==1:
        state=bits[0]
        if _is_thumbs_up(hands[0].points,state):return Gesture('THUMBS_UP',conf,state)
        if not any(state):return Gesture('FIST',conf,state)
        # Canonical, intentionally not every possible shape with equal finger count.
        number_patterns={1:(False,True,False,False,False),
                         2:(False,True,True,False,False),
                         3:(False,True,True,True,False),
                         4:(False,True,True,True,True),
                         5:(True,True,True,True,True)}
        for n,pat in number_patterns.items():
            if state==pat:return Gesture(str(n),conf,state)
        return UNKNOWN
    # Two hands: only one all-five plus a canonical 1..5 hand.
    # A mixed pair with a fist never fires FIST or an ambiguous single-hand number.
    single={1:(False,True,False,False,False),2:(False,True,True,False,False),
            3:(False,True,True,True,False),4:(False,True,True,True,True),
            5:(True,True,True,True,True)}
    five=single[5]
    for first,second in ((0,1),(1,0)):
        if bits[first]==five:
            for extra,pattern in single.items():
                if bits[second]==pattern:return Gesture(str(5+extra),conf,())
    return UNKNOWN
