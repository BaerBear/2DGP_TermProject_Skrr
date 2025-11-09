from pico2d import *
from Image_Loader import Enemy_Image_Loader
import SKRR
import random
import game_framework

ENEMY_WALK_SPEED_PPS = 100.0

class Enemy:
    IDLE_TIME_PER_ACTION = 0.167
    IDLE_ACTION_PER_TIME = 1.0 / IDLE_TIME_PER_ACTION
    IDLE_FRAMES_PER_ACTION = 10

    WALK_TIME_PER_ACTION = 0.1
    WALK_ACTION_PER_TIME = 1.0 / WALK_TIME_PER_ACTION
    WALK_FRAMES_PER_ACTION = 6

    ATTACK_TIME_PER_ACTION = 0.1
    ATTACK_ACTION_PER_TIME = 1.0 / ATTACK_TIME_PER_ACTION
    ATTACK_FRAMES_PER_ACTION = 6

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.frame = 0
        self.frame_time = 0
        self.face_dir = -1 if random.randint(-100, 100) < 0 else 1
        self.scale = 2
        self.is_alive = True

        # 임의 스탯
        self.hp = 150
        self.velocity = ENEMY_WALK_SPEED_PPS
        self.dis_to_player = 0

        self.is_attacking = False
        self.is_hit = False
        self.attack_cooldown_time = 1.5
        self.attack_last_use_time = 0
        self.state = 'IDLE'
        self.prev_state = 'IDLE'

    def update(self):
        if not self.is_alive:
            return

        player = SKRR.get_player()
        if player:
            self.dis_to_player = abs(self.x - player.x)

            if player.x > self.x:
                self.face_dir = 1
            else:
                self.face_dir = -1

            attack_range = 100
            detect_range = 400

            current_time = get_time()

            if self.dis_to_player <= attack_range:
                if current_time - self.attack_last_use_time >= self.attack_cooldown_time:
                    self.state = 'ATTACK'
                    self.is_attacking = True
                    self.attack_last_use_time = current_time
                elif not self.is_attacking:
                    self.state = 'IDLE'
            elif self.dis_to_player <= detect_range:
                self.state = 'WALK'
                self.x += self.velocity * self.face_dir * game_framework.frame_time
            else:
                self.state = 'IDLE'

        if self.state != self.prev_state:
            self.frame_time = 0
            self.prev_state = self.state

        self.frame_time += game_framework.frame_time

        if self.state == 'IDLE':
            self.frame = int(self.frame_time * self.IDLE_ACTION_PER_TIME * self.IDLE_FRAMES_PER_ACTION)
        elif self.state == 'WALK':
            self.frame = int(self.frame_time * self.WALK_ACTION_PER_TIME * self.WALK_FRAMES_PER_ACTION)
        elif self.state == 'ATTACK':
            self.frame = int(self.frame_time * self.ATTACK_ACTION_PER_TIME * self.ATTACK_FRAMES_PER_ACTION)

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
                img = Knight_Sword.images['dead'][int(self.frame_time * self.ATTACK_ACTION_PER_TIME) % len(Knight_Sword.images['dead'])]
            else:
                return
        elif self.state == 'ATTACK':
            if 'attack' in Knight_Sword.images and Knight_Sword.images['attack']:
                img = Knight_Sword.images['attack'][int(self.frame_time * self.ATTACK_ACTION_PER_TIME) % len(Knight_Sword.images['attack'])]
            else:
                return
        elif self.state == 'WALK':
            if 'walk' in Knight_Sword.images and Knight_Sword.images['walk']:
                img = Knight_Sword.images['walk'][int(self.frame_time * self.WALK_ACTION_PER_TIME) % len(Knight_Sword.images['walk'])]
            else:
                return
        else:
            if 'idle' in Knight_Sword.images and Knight_Sword.images['idle']:
                img = Knight_Sword.images['idle'][int(self.frame_time * self.IDLE_ACTION_PER_TIME) % len(Knight_Sword.images['idle'])]
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
                img = Knight_Bow.images['dead'][int(self.frame_time * self.ATTACK_ACTION_PER_TIME) % len(Knight_Bow.images['dead'])]
            else:
                return
        elif self.state == 'ATTACK':
            if 'attack' in Knight_Bow.images and Knight_Bow.images['attack']:
                img = Knight_Bow.images['attack'][int(self.frame_time * self.ATTACK_ACTION_PER_TIME) % len(Knight_Bow.images['attack'])]
            else:
                return
        elif self.state == 'WALK':
            if 'walk' in Knight_Bow.images and Knight_Bow.images['walk']:
                img = Knight_Bow.images['walk'][int(self.frame_time * self.WALK_ACTION_PER_TIME) % len(Knight_Bow.images['walk'])]
            else:
                return
        else:
            if 'idle' in Knight_Bow.images and Knight_Bow.images['idle']:
                img = Knight_Bow.images['idle'][int(self.frame_time * self.IDLE_ACTION_PER_TIME) % len(Knight_Bow.images['idle'])]
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
                img = Knight_Tackle.images['dead'][int(self.frame_time * self.ATTACK_ACTION_PER_TIME) % len(Knight_Tackle.images['dead'])]
            else:
                return
        elif self.state == 'ATTACK':
            if 'attack' in Knight_Tackle.images and Knight_Tackle.images['attack']:
                img = Knight_Tackle.images['attack'][int(self.frame_time * self.ATTACK_ACTION_PER_TIME) % len(Knight_Tackle.images['attack'])]
            else:
                return
        elif self.state == 'TACKLE':
            if 'tackle' in Knight_Tackle.images and Knight_Tackle.images['tackle']:
                img = Knight_Tackle.images['tackle'][int(self.frame_time * self.ATTACK_ACTION_PER_TIME) % len(Knight_Tackle.images['tackle'])]
            else:
                return
        elif self.state == 'WALK':
            if 'walk' in Knight_Tackle.images and Knight_Tackle.images['walk']:
                img = Knight_Tackle.images['walk'][int(self.frame_time * self.WALK_ACTION_PER_TIME) % len(Knight_Tackle.images['walk'])]
            else:
                return
        else:
            if 'idle' in Knight_Tackle.images and Knight_Tackle.images['idle']:
                img = Knight_Tackle.images['idle'][int(self.frame_time * self.IDLE_ACTION_PER_TIME) % len(Knight_Tackle.images['idle'])]
            else:
                return

        if self.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.x, self.y, img.w * self.scale, img.h * self.scale)
        else:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.x, self.y, img.w * self.scale, img.h * self.scale)
