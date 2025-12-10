from pico2d import *
import game_framework

class Camera:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Camera()
        return cls._instance

    def __init__(self):
        self.x = 0
        self.y = 0
        self.target = None

        self.min_x = 0
        self.max_x = 10000
        self.min_y = 0
        self.max_y = 10000

        self.smoothness = 0.1

    def set_target(self, target):
        self.target = target

    def set_bounds(self, min_x, max_x, min_y, max_y):
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    def update(self):
        if self.target:
            target_x = self.target.x - game_framework.width // 2
            target_y = self.target.y - game_framework.height // 2

            self.x += (target_x - self.x) * self.smoothness
            self.y += (target_y - self.y) * self.smoothness

            self.x = max(self.min_x, min(self.x, self.max_x - game_framework.width))
            self.y = max(self.min_y, min(self.y, self.max_y - game_framework.height))

    def apply(self, x, y):
        return x - self.x, y - self.y

    def get_position(self):
        return self.x, self.y

