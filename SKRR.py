from pico2d import *

class IDLE:
    def __init__(self, skrr):
        self.skrr = skrr

    def enter(self):
        self.skrr.frame = 0

    def do(self):
        self.skrr.frame += 1

    def exit(self):
        pass

    def draw(self):
        if self.skrr.face_dir == 1:
            pass
        else:
            pass

class SKRR:
    def __init__(self):
        self.x, self.y = get_canvas_width() // 2, get_canvas_height() // 2
        self.frame = 0
        self.face_dir = 1

    def update(self):
        pass

    def draw(self):
        pass
