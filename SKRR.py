from pico2d import *
from Image_Loader import SKRR_Image_Loader

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
        img = self.skrr.Idle_image[self.skrr.frame // 10 % 4]
        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y,
                          img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y,
                                    img.w * self.skrr.scale, img.h * self.skrr.scale)


class SKRR:
    def __init__(self):
        self.x, self.y = get_canvas_width() // 2, get_canvas_height() // 2
        self.frame = 0
        self.face_dir = 1

        self.Idle_image = SKRR_Image_Loader('Idle').images

    def update(self):
        pass

    def draw(self):
        pass
