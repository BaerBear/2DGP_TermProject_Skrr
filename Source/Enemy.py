from pico2d import *
from Image_Loader import Enemy_Image_Loader
import SKRR
import random

class Enemy:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.frame = random.randint(0,3)
        self.face_dir = -1 if random.randint(-100, 100) < 0 else 1
        self.scale = 2
        self.is_alive = True

        # 임의 스탯
        self.hp = 150
        self.velocity = 5
        self.dis_to_player = 0

        self.is_attacking = False
        self.is_hit = False
        self.attack_cooldown_time = 1.5  # 공격 쿨타임
        self.attack_last_use_time = 0
        self.state = 'IDLE'

    def update(self):
        if not self.is_alive:
            return

        # 플레이어와의 거리
        player = SKRR.get_player()
        if player:
            pass

        self.frame += 1

    def draw(self):
        pass

class Knight_Sword(Enemy):
    images = None

    def __init__(self, x, y):
        super().__init__(x, y)
        if not Knight_Sword.images:
            Knight_Sword.images = {}
            Knight_Sword.images['walk'] = Enemy_Image_Loader('Knight_Sword', 'Walk').images
            Knight_Sword.images['attack'] = Enemy_Image_Loader('Knight_Sword', 'Attack').images
            Knight_Sword.images['hit'] = Enemy_Image_Loader('Knight_Sword', 'Hit').images
            Knight_Sword.images['idle'] = Enemy_Image_Loader('Knight_Sword', 'Idle').images

    def update(self):
        super().update()

    def draw(self):
        if not self.is_alive:
            if 'dead' in Knight_Sword.images and Knight_Sword.images['dead']:
                img = Knight_Sword.images['dead'][(self.frame // 3) % len(Knight_Sword.images['dead'])]
            else:
                return
        elif self.state == 'ATTACK':
            if 'attack' in Knight_Sword.images and Knight_Sword.images['attack']:
                img = Knight_Sword.images['attack'][(self.frame // 3) % len(Knight_Sword.images['attack'])]
            else:
                return
        elif self.state == 'WALK':
            if 'walk' in Knight_Sword.images and Knight_Sword.images['walk']:
                img = Knight_Sword.images['walk'][(self.frame // 3) % len(Knight_Sword.images['walk'])]
            else:
                return
        else:
            if 'idle' in Knight_Sword.images and Knight_Sword.images['idle']:
                img = Knight_Sword.images['idle'][(self.frame // 10) % len(Knight_Sword.images['idle'])]
            else:
                return

        if self.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.x, self.y, img.w * self.scale, img.h * self.scale)
        else:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.x, self.y, img.w * self.scale, img.h * self.scale)


class Knight_Bow(Enemy):
    images = None

    def __init__(self, x, y):
        super().__init__(x, y)
        if not Knight_Bow.images:
            Knight_Bow.images = {}
            Knight_Bow.images['walk'] = Enemy_Image_Loader('Knight_Bow', 'Walk').images
            Knight_Bow.images['attack'] = Enemy_Image_Loader('Knight_Bow', 'Attack').images
            Knight_Bow.images['hit'] = Enemy_Image_Loader('Knight_Bow', 'Hit').images
            Knight_Bow.images['idle'] = Enemy_Image_Loader('Knight_Bow', 'Idle').images

    def update(self):
        super().update()

    def draw(self):
        if not self.is_alive:
            if 'dead' in Knight_Bow.images and Knight_Bow.images['dead']:
                img = Knight_Bow.images['dead'][(self.frame // 3) % len(Knight_Bow.images['dead'])]
            else:
                return
        elif self.state == 'ATTACK':
            if 'attack' in Knight_Bow.images and Knight_Bow.images['attack']:
                img = Knight_Bow.images['attack'][(self.frame // 3) % len(Knight_Bow.images['attack'])]
            else:
                return
        elif self.state == 'WALK':
            if 'walk' in Knight_Bow.images and Knight_Bow.images['walk']:
                img = Knight_Bow.images['walk'][(self.frame // 3) % len(Knight_Bow.images['walk'])]
            else:
                return
        else:
            if 'idle' in Knight_Bow.images and Knight_Bow.images['idle']:
                img = Knight_Bow.images['idle'][(self.frame // 10) % len(Knight_Bow.images['idle'])]
            else:
                return

        if self.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.x, self.y, img.w * self.scale, img.h * self.scale)
        else:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.x, self.y, img.w * self.scale, img.h * self.scale)


class Knight_Tackle(Enemy):
    images = None

    def __init__(self, x, y):
        super().__init__(x, y)
        if not Knight_Tackle.images:
            Knight_Tackle.images = {}
            Knight_Tackle.images['walk'] = Enemy_Image_Loader('Knight_Tackle', 'Walk').images
            Knight_Tackle.images['attack'] = Enemy_Image_Loader('Knight_Tackle', 'Attack').images
            Knight_Tackle.images['tackle'] = Enemy_Image_Loader('Knight_Tackle', 'Tackle').images
            Knight_Tackle.images['idle'] = Enemy_Image_Loader('Knight_Tackle', 'Idle').images

    def update(self):
        super().update()

    def draw(self):
        if not self.is_alive:
            if 'dead' in Knight_Tackle.images and Knight_Tackle.images['dead']:
                img = Knight_Tackle.images['dead'][(self.frame // 3) % len(Knight_Tackle.images['dead'])]
            else:
                return
        elif self.state == 'ATTACK':
            if 'attack' in Knight_Tackle.images and Knight_Tackle.images['attack']:
                img = Knight_Tackle.images['attack'][(self.frame // 3) % len(Knight_Tackle.images['attack'])]
            else:
                return
        elif self.state == 'TACKLE':
            if 'tackle' in Knight_Tackle.images and Knight_Tackle.images['tackle']:
                img = Knight_Tackle.images['tackle'][(self.frame // 3) % len(Knight_Tackle.images['tackle'])]
            else:
                return
        elif self.state == 'WALK':
            if 'walk' in Knight_Tackle.images and Knight_Tackle.images['walk']:
                img = Knight_Tackle.images['walk'][(self.frame // 3) % len(Knight_Tackle.images['walk'])]
            else:
                return
        else:
            if 'idle' in Knight_Tackle.images and Knight_Tackle.images['idle']:
                img = Knight_Tackle.images['idle'][(self.frame // 10) % len(Knight_Tackle.images['idle'])]
            else:
                return

        if self.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.x, self.y, img.w * self.scale, img.h * self.scale)
        else:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.x, self.y, img.w * self.scale, img.h * self.scale)

