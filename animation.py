import pygame

class Animation:
    def __init__(self, frames, speed=10, loop=True):
        self.frames = frames
        self.speed = speed  
        self.loop = loop
        self.current_frame = 0
        self.done = False
        self.frame_counter = 0
    
    def update(self):
        if not self.done:
            self.frame_counter += 1
            if self.frame_counter >= self.speed:
                self.frame_counter = 0
                self.current_frame += 1
                
                if self.current_frame >= len(self.frames):
                    if self.loop:
                        self.current_frame = 0
                    else:
                        self.current_frame = len(self.frames) - 1
                        self.done = True
    
    def get_current_frame(self):
        if self.frames:
            return self.frames[self.current_frame]
        return None
    
    def reset(self):
        self.current_frame = 0
        self.frame_counter = 0
        self.done = False
    
    def is_finished(self):
        return self.done and not self.loop
