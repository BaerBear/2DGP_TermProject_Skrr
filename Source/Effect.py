from pico2d import *
from ResourceManager import ResourceManager
import game_framework

TIME_PER_ACTION = 0.3
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION


class HitEffect:
    images = {}

    def __init__(self, effect_type, x, y, scale=1.0):
        self.effect_type = effect_type
        if effect_type not in HitEffect.images:
            HitEffect.images[effect_type] = ResourceManager.get_effect_images(effect_type)
        self.images = HitEffect.images[effect_type]
        self.FRAMES_PER_ACTION = len(self.images)
        self.x = x
        self.y = y
        self.scale = scale
        self.frame = 0
        self.done = False
        self.alpha = 1.0

    def update(self):
        if not self.done:
            self.frame += game_framework.frame_time * self.FRAMES_PER_ACTION * ACTION_PER_TIME
            if self.frame >= self.FRAMES_PER_ACTION:
                self.done = True
            else:
                self.alpha = 1.0 - (self.frame / self.FRAMES_PER_ACTION)

    def draw(self):
        if not self.done:
            frame_index = int(self.frame)
            if frame_index < len(self.images):
                image = self.images[frame_index]
                image.opacify(self.alpha)
                image.composite_draw(0, '', self.x, self.y,
                                     int(image.w * self.scale),
                                     int(image.h * self.scale))

    def is_done(self):
        return self.done
