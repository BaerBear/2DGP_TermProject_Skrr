from pico2d import *
from ResourceManager import ResourceManager
import game_framework

TIME_PER_ACTION = 0.3
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION

class Effect:
    images = None
    def __init__(self, effect_type, x, y):
        self.effect_type = effect_type
        if Effect.images is None:
            Effect.images = ResourceManager.get_effect_images(effect_type)
        self.FRAMES_PER_ACTION = len(self.images)
        self.x = x
        self.y = y
        self.frame = 0
        self.done = False

    def update(self):
        if not self.done:
            self.frame += int(game_framework.frame_time * self.FRAMES_PER_ACTION * ACTION_PER_TIME)
            if self.frame >= len(self.images):
                self.done = True

    def draw(self):
        if not self.done:
            image = self.images[self.frame]
            image.draw(self.x, self.y)