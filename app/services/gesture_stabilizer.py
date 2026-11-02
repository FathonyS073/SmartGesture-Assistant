"""Temporal gesture debounce and held-pose latching."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class GestureStabilizer:
    duration:float=.8
    min_frames:int=4
    min_confidence:float=.55
    release_seconds:float=.18
    def __post_init__(self):self.reset()
    def reset(self):
        self.candidate='UNKNOWN';self.since=0.;self.frames=0
        self.latched='UNKNOWN';self.neutral_since=None
    def feed(self,label:str,confidence:float,at:float)->str|None:
        if confidence<self.min_confidence:label='UNKNOWN'
        if label=='UNKNOWN':
            # Any interrupted observation resets the continuous-duration candidate;
            # the latched command only rearms after a sustained neutral interval.
            self.candidate='UNKNOWN';self.frames=0
            if self.neutral_since is None:self.neutral_since=at
            if at-self.neutral_since>=self.release_seconds:
                self.candidate='UNKNOWN';self.frames=0;self.latched='UNKNOWN'
            return None
        self.neutral_since=None
        if label!=self.candidate:
            self.candidate=label;self.since=at;self.frames=1
        else:
            self.frames+=1
        if (self.frames>=self.min_frames and at-self.since>=self.duration
                and label!=self.latched):
            self.latched=label
            return label
        return None
