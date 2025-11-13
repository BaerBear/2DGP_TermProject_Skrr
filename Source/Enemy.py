from pico2d import *
from ResourceManager import ResourceManager
import SKRR
import random
import game_framework
import game_world

ENEMY_WALK_SPEED_PPS = 100.0

class Enemy:
    dead_effect = None
    hit_effect = None

    IDLE_TIME_PER_ACTION = 0.167
    IDLE_ACTION_PER_TIME = 1.0 / IDLE_TIME_PER_ACTION
    IDLE_FRAMES_PER_ACTION = 10

    WALK_TIME_PER_ACTION = 0.1
    WALK_ACTION_PER_TIME = 1.0 / WALK_TIME_PER_ACTION
    WALK_FRAMES_PER_ACTION = 6

    ATTACK_TIME_PER_ACTION = 0.1
    ATTACK_ACTION_PER_TIME = 1.0 / ATTACK_TIME_PER_ACTION
    ATTACK_FRAMES_PER_ACTION = 6

    @classmethod
    def load_common_effects(cls):
        if cls.dead_effect is None:
            cls.dead_effect = ResourceManager.get_effect_images('enemy_dead')
        if cls.hit_effect is None:
            cls.hit_effect = ResourceManager.get_effect_images('hit_effect')

    def __init__(self, x, y):
        Enemy.load_common_effects()

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
        self.hp = 150
        self.velocity = ENEMY_WALK_SPEED_PPS
        self.attack_cooldown_time = 1.5
        if not Knight_Sword.images:
            Knight_Sword.images = ResourceManager.get_enemy_images('Knight_Sword')

    def update(self):
        super().update()

        if self.state == 'ATTACK':
            attack_duration = len(Knight_Sword.images.get('attack', [])) * self.ATTACK_TIME_PER_ACTION
            if self.frame_time >= attack_duration:
                self.is_attacking = False

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

        cam_x, cam_y = self.x, self.y
        if game_world.camera:
            cam_x, cam_y = game_world.camera.apply(self.x, self.y)

        if self.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, cam_x, cam_y, img.w * self.scale, img.h * self.scale)
        else:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', cam_x, cam_y, img.w * self.scale, img.h * self.scale)


class Knight_Bow(Enemy):
    images = None

    def __init__(self, x, y):
        super().__init__(x, y)
        self.hp = 100
        self.velocity = ENEMY_WALK_SPEED_PPS * 0.8
        self.attack_cooldown_time = 2.0
        self.preferred_distance = 250
        self.is_aiming = False
        self.aim_duration = 1.0
        self.aim_timer = 0
        self.aim_frames = 4
        if not Knight_Bow.images:
            Knight_Bow.images = ResourceManager.get_enemy_images('Knight_Bow')

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

            attack_range_min = 150
            attack_range_max = 350
            detect_range = 500

            current_time = get_time()

            if self.is_aiming:
                self.state = 'AIM'
                self.aim_timer += game_framework.frame_time
                if self.aim_timer >= self.aim_duration:
                    self.state = 'ATTACK'
                    self.is_aiming = False
                    self.is_attacking = True
                    self.aim_timer = 0
                    self.attack_last_use_time = current_time
            elif current_time - self.attack_last_use_time >= self.attack_cooldown_time and not self.is_attacking:
                if self.dis_to_player <= detect_range:
                    self.is_aiming = True
                    self.aim_timer = 0
                    self.state = 'AIM'
            elif not self.is_attacking and not self.is_aiming:
                if self.dis_to_player < attack_range_min:
                    self.state = 'WALK'
                    self.x -= self.velocity * self.face_dir * game_framework.frame_time  # 반대로 이동
                elif self.dis_to_player > attack_range_max and self.dis_to_player <= detect_range:
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
        elif self.state == 'AIM':
            aim_progress = self.aim_timer / self.aim_duration
            self.frame = min(int(aim_progress * self.aim_frames), self.aim_frames - 1)
        elif self.state == 'ATTACK':
            # 공격 중에는 3번 프레임 고정
            self.frame = 3
            attack_duration = len(Knight_Bow.images.get('attack', [])) * self.ATTACK_TIME_PER_ACTION
            if self.frame_time >= attack_duration:
                self.is_attacking = False

    def draw(self):
        if not self.is_alive:
            if 'dead' in Knight_Bow.images and Knight_Bow.images['dead']:
                img = Knight_Bow.images['dead'][int(self.frame_time * self.ATTACK_ACTION_PER_TIME) % len(Knight_Bow.images['dead'])]
            else:
                return
        elif self.state == 'AIM':
            if 'attack' in Knight_Bow.images and Knight_Bow.images['attack']:
                if self.frame < len(Knight_Bow.images['attack']):
                    img = Knight_Bow.images['attack'][self.frame]
                else:
                    img = Knight_Bow.images['attack'][0]
            else:
                return
        elif self.state == 'ATTACK':
            if 'attack' in Knight_Bow.images and Knight_Bow.images['attack']:
                if 3 < len(Knight_Bow.images['attack']):
                    img = Knight_Bow.images['attack'][3]
                else:
                    img = Knight_Bow.images['attack'][0]
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

        cam_x, cam_y = self.x, self.y
        if game_world.camera:
            cam_x, cam_y = game_world.camera.apply(self.x, self.y)

        if self.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, cam_x, cam_y, img.w * self.scale, img.h * self.scale)
        else:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', cam_x, cam_y, img.w * self.scale, img.h * self.scale)


class Knight_Tackle(Enemy):
    images = None

    def __init__(self, x, y):
        super().__init__(x, y)
        self.hp = 200
        self.velocity = ENEMY_WALK_SPEED_PPS * 1.2
        self.attack_cooldown_time = 3.0
        self.tackle_cooldown_time = 7.0
        self.tackle_last_use_time = -7.0
        self.is_tackling = False
        self.is_tackle_ready = False
        self.is_tackle_end = False
        self.tackle_ready_duration = 1.0
        self.tackle_ready_timer = 0
        self.tackle_end_duration = 0.3
        self.tackle_end_timer = 0
        self.tackle_speed = ENEMY_WALK_SPEED_PPS * 3.0
        self.tackle_distance = 400
        self.tackle_traveled = 0
        if not Knight_Tackle.images:
            Knight_Tackle.images = ResourceManager.get_enemy_images('Knight_Tackle')

    def update(self):
        if not self.is_alive:
            return

        player = SKRR.get_player()
        if player:
            self.dis_to_player = abs(self.x - player.x)

            if not self.is_tackling:
                if player.x > self.x:
                    self.face_dir = 1
                else:
                    self.face_dir = -1

            current_time = get_time()

            if self.is_tackle_ready:
                self.state = 'TACKLE_READY'
                self.tackle_ready_timer += game_framework.frame_time

                if self.tackle_ready_timer >= self.tackle_ready_duration:
                    self.is_tackle_ready = False
                    self.is_tackling = True
                    self.tackle_ready_timer = 0
                    self.tackle_traveled = 0
                    self.state = 'TACKLE'
            elif self.is_tackling:
                self.state = 'TACKLE'
                move_distance = self.tackle_speed * game_framework.frame_time
                self.x += move_distance * self.face_dir
                self.tackle_traveled += move_distance

                if self.tackle_traveled >= self.tackle_distance:
                    self.is_tackling = False
                    self.is_tackle_end = True
                    self.tackle_traveled = 0
                    self.tackle_end_timer = 0
                    self.state = 'TACKLE_END'
            elif self.is_tackle_end:
                self.state = 'TACKLE_END'
                self.tackle_end_timer += game_framework.frame_time

                if self.tackle_end_timer >= self.tackle_end_duration:
                    self.is_tackle_end = False
                    self.tackle_end_timer = 0
                    self.tackle_last_use_time = current_time
                    self.state = 'IDLE'
            else:
                detect_range = 500
                if current_time - self.tackle_last_use_time >= self.tackle_cooldown_time:
                    if self.dis_to_player <= detect_range:
                        self.is_tackle_ready = True
                        self.tackle_ready_timer = 0
                        self.state = 'TACKLE_READY'
                        return
                attack_range = 80
                detect_range_normal = 400

                if self.dis_to_player <= attack_range:
                    if current_time - self.attack_last_use_time >= self.attack_cooldown_time:
                        self.state = 'ATTACK'
                        self.is_attacking = True
                        self.attack_last_use_time = current_time
                    elif not self.is_attacking:
                        self.state = 'IDLE'
                elif self.dis_to_player <= detect_range_normal:
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
            attack_duration = len(Knight_Tackle.images.get('attack', [])) * self.ATTACK_TIME_PER_ACTION
            if self.frame_time >= attack_duration:
                self.is_attacking = False
        elif self.state == 'TACKLE_READY':
            self.frame = 0
        elif self.state == 'TACKLE':
            self.frame = 1
        elif self.state == 'TACKLE_END':
            self.frame = 2

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
        elif self.state in ['TACKLE_READY', 'TACKLE', 'TACKLE_END']:
            if 'tackle' in Knight_Tackle.images and Knight_Tackle.images['tackle']:
                if self.frame < len(Knight_Tackle.images['tackle']):
                    img = Knight_Tackle.images['tackle'][self.frame]
                else:
                    img = Knight_Tackle.images['tackle'][0]
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

        cam_x, cam_y = self.x, self.y
        if game_world.camera:
            cam_x, cam_y = game_world.camera.apply(self.x, self.y)

        if self.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, cam_x, cam_y, img.w * self.scale, img.h * self.scale)
        else:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', cam_x, cam_y, img.w * self.scale, img.h * self.scale)
