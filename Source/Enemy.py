from pico2d import *
from Image_Loader import Enemy_Image_Loader
import random

class Enemy:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.frame = 0
        self.face_dir = -1 if random.randint(-100, 100) < 0 else 1
        self.scale = 2

        self.is_attacking = False
        self.is_hit = False
        self.attack_cooldown_time = 1.5  # 공격 쿨타임
        self.attack_last_use_time = 0
        self.state = 'IDLE'

    def update(self):
        pass

    def draw(self):
        pass

