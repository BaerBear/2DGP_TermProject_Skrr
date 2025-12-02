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

    ATTACK_TIME_PER_ACTION = 0.15
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

        # 물리 속성 추가
        self.velocity_y = 0
        self.gravity = -1000
        self.is_grounded = False
        self.tile_map = None

        self.width = 30 * self.scale
        self.height = 40 * self.scale

    def set_tile_map(self, tile_map):
        """타일맵 설정"""
        self.tile_map = tile_map

    def get_bb(self):
        """충돌 박스 반환 (타일 충돌, 물리 처리용)"""
        return (self.x - self.width / 2, self.y - self.height / 2,
                self.x + self.width / 2, self.y + self.height / 2)

    def get_hit_bb(self):
        """피격 박스 반환 (플레이어 공격 받을 때 사용)"""
        return self.get_bb()

    def apply_gravity(self):
        """중력 적용"""
        if not self.is_grounded:
            self.velocity_y += self.gravity * game_framework.frame_time
            self.y += self.velocity_y * game_framework.frame_time

    def check_tile_collision(self):
        """타일맵과의 충돌 체크"""
        if not self.tile_map:
            return

        left, bottom, right, top = self.get_bb()
        colliding_tiles = self.tile_map.check_collision(left, bottom, right, top)

        has_ground_collision = False

        for tile in colliding_tiles:
            if tile['layer'] == 'tile':
                if self.handle_tile_collision(tile):
                    has_ground_collision = True
            elif tile['layer'] == 'flatform':
                if self.handle_platform_collision(tile):
                    has_ground_collision = True

        was_grounded = self.is_grounded
        self.is_grounded = has_ground_collision

        if self.is_grounded and not was_grounded:
            self.velocity_y = 0

    def handle_tile_collision(self, tile):
        """타일과의 충돌 처리"""
        left, bottom, right, top = self.get_bb()

        overlap_left = right - tile['left']
        overlap_right = tile['right'] - left
        overlap_top = tile['top'] - bottom
        overlap_bottom = top - tile['bottom']

        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

        # 천장 충돌
        if min_overlap == overlap_bottom and self.velocity_y > 0:
            horizontal_overlap = min(overlap_left, overlap_right)
            if horizontal_overlap > self.width * 0.5:
                self.y = tile['bottom'] - self.height / 2
                self.velocity_y = 0
                return False
        # 바닥 충돌
        elif min_overlap == overlap_top and self.velocity_y <= 0:
            self.y = tile['top'] + self.height / 2
            self.velocity_y = 0
            return True
        # 왼쪽 벽 충돌
        elif min_overlap == overlap_left:
            self.x = tile['left'] - self.width / 2
            return False
        # 오른쪽 벽 충돌
        elif min_overlap == overlap_right:
            self.x = tile['right'] + self.width / 2
            return False

        return False

    def handle_platform_collision(self, tile):
        """플랫폼과의 충돌 처리"""
        left, bottom, right, top = self.get_bb()

        if self.velocity_y <= 0 and bottom <= tile['top'] and bottom >= tile['top'] - 10:
            self.y = tile['top'] + self.height / 2
            self.velocity_y = 0
            return True

        return False

    def update(self):
        if not self.is_alive:
            return

        self.apply_gravity()

        player = SKRR.get_player()
        if player:
            self.dis_to_player = abs(self.x - player.x)

            # 공격 중이 아닐 때만 방향 전환
            if not self.is_attacking:
                if player.x > self.x:
                    self.face_dir = 1
                else:
                    self.face_dir = -1

            attack_range = 100
            detect_range = 400

            current_time = get_time()

            # 공격 중이면 범위와 관계없이 공격 완료까지 진행
            if self.is_attacking:
                self.state = 'ATTACK'
            # 감지 범위 내에서만 새로운 행동 시작
            elif self.dis_to_player <= detect_range:
                if self.dis_to_player <= attack_range:
                    if current_time - self.attack_last_use_time >= self.attack_cooldown_time:
                        self.state = 'ATTACK'
                        self.is_attacking = True
                        self.attack_last_use_time = current_time
                    else:
                        self.state = 'IDLE'
                else:
                    self.state = 'WALK'
                    self.x += self.velocity * self.face_dir * game_framework.frame_time
            else:
                # 감지 범위 밖이면 IDLE
                self.state = 'IDLE'

        # 맵 경계 체크
        if self.tile_map:
            map_width_pixels = self.tile_map.map_width * self.tile_map.tile_width
            if self.x < self.width / 2:
                self.x = self.width / 2
            elif self.x > map_width_pixels - self.width / 2:
                self.x = map_width_pixels - self.width / 2

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

        self.check_tile_collision()

    def draw(self):
        pass

    def draw_collision_box(self):
        """충돌 박스 그리기 (디버그용)"""
        if SKRR.SKRR.show_collision_box:
            from pico2d import draw_rectangle
            if game_world.camera:
                camera_x, camera_y = game_world.camera.get_position()
                left, bottom, right, top = self.get_bb()
                draw_rectangle(left - camera_x, bottom - camera_y,
                             right - camera_x, top - camera_y)

class Knight_Sword(Enemy):
    images = None

    def __init__(self, x, y):
        super().__init__(x, y)
        self.hp = 150
        self.velocity = ENEMY_WALK_SPEED_PPS
        self.attack_cooldown_time = 1.5

        if not Knight_Sword.images:
            Knight_Sword.images = ResourceManager.get_enemy_images('Knight_Sword')

        if Knight_Sword.images and 'idle' in Knight_Sword.images and Knight_Sword.images['idle']:
            sample_img = Knight_Sword.images['idle'][0]
            self.width = sample_img.w * self.scale * 0.8
            self.height = sample_img.h * self.scale
        else:
            self.width = 25 * self.scale
            self.height = 35 * self.scale

    def get_bb(self):
        return (self.x - self.width / 2, self.y - self.height / 2,
                self.x + self.width / 2, self.y + self.height / 3)

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

        if self.state == 'WALK':
            offset_y = 8
        else:
            offset_y = 0

        if self.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, cam_x, cam_y - offset_y, img.w * self.scale, img.h * self.scale)
        else:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', cam_x, cam_y- offset_y, img.w * self.scale, img.h * self.scale)

        self.draw_collision_box()


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
        
        self.sign_frame = 0
        self.SIGN_TIME_PER_ACTION = 1.5
        self.SIGN_ACTION_PER_TIME = 1.0 / self.SIGN_TIME_PER_ACTION
        self.SIGN_FRAMES_PER_ACTION = 17

        if not Knight_Bow.images:
            Knight_Bow.images = ResourceManager.get_enemy_images('Knight_Bow')

        if Knight_Bow.images and 'idle' in Knight_Bow.images and Knight_Bow.images['idle']:
            sample_img = Knight_Bow.images['idle'][0]
            self.width = sample_img.w * self.scale * 0.6
            self.height = sample_img.h * self.scale
        else:
            self.width = 22 * self.scale
            self.height = 32 * self.scale

    def get_bb(self):
        return (self.x - self.width / 2, self.y - self.height / 2,
                self.x + self.width / 2, self.y + self.height / 3)

    def update(self):
        if not self.is_alive:
            return

        self.apply_gravity()
        self.check_tile_collision()

        player = SKRR.get_player()
        if player:
            self.dis_to_player = abs(self.x - player.x)

            if not self.is_attacking and self.state != 'AIM':
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
                    self.sign_frame = 0
            elif not self.is_attacking and not self.is_aiming:
                if self.dis_to_player < attack_range_min:
                    self.state = 'WALK'
                    self.x -= self.velocity * self.face_dir * game_framework.frame_time
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
            self.sign_frame = int(self.frame_time * self.SIGN_ACTION_PER_TIME * self.SIGN_FRAMES_PER_ACTION)
        elif self.state == 'ATTACK':
            self.frame = 3
            attack_duration = len(Knight_Bow.images.get('attack', [])) * self.ATTACK_TIME_PER_ACTION
            self.sign_frame = int(self.frame_time * self.SIGN_ACTION_PER_TIME * self.SIGN_FRAMES_PER_ACTION)
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

        sign_img = Knight_Bow.images['attack_sign'][self.sign_frame]

        cam_x, cam_y = self.x, self.y
        if game_world.camera:
            cam_x, cam_y = game_world.camera.apply(self.x, self.y)

        if self.state == 'ATTACK' or self.state == 'AIM':
            offset_y = 8
        else:
            offset_y = 0

        if self.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, cam_x, cam_y - offset_y, img.w * self.scale, img.h * self.scale)
            if self.state == 'ATTACK' or self.state == 'AIM':
                sign_img.clip_draw(0, 0, sign_img.w, sign_img.h,
                                   cam_x + sign_img.w * self.scale / 2, cam_y, sign_img.w * self.scale, sign_img.h/ 2)
        else:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', cam_x, cam_y - offset_y, img.w * self.scale, img.h * self.scale)
            if self.state == 'ATTACK' or self.state == 'AIM':
                sign_img.clip_composite_draw(0, 0, sign_img.w, sign_img.h, 0, 'h',
                                             cam_x - sign_img.w * self.scale / 2, cam_y, sign_img.w * self.scale, sign_img.h / 2)

        self.draw_collision_box()


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

        if Knight_Tackle.images and 'idle' in Knight_Tackle.images and Knight_Tackle.images['idle']:
            sample_img = Knight_Tackle.images['idle'][0]
            self.width = sample_img.w * self.scale * 0.7
            self.height = sample_img.h * self.scale
        else:
            self.width = 30 * self.scale
            self.height = 40 * self.scale

    def get_bb(self):
        if self.is_tackling:
            width_modifier = 0.9
        else:
            width_modifier = 1.0

        adjusted_width = self.width * width_modifier
        return (self.x - adjusted_width / 2, self.y - self.height / 2,
                self.x + adjusted_width / 2, self.y + self.height / 4)

    def get_hit_bb(self):
        if self.is_tackling:
            width_modifier = 0.9
            adjusted_width = self.width * width_modifier
            body_offset = -10 * self.face_dir

            return (self.x + body_offset - adjusted_width / 2, self.y - self.height / 2,
                    self.x + body_offset + adjusted_width / 2, self.y + self.height / 4 - 10)
        else:
            if (self.face_dir == 1):
                return (self.x - self.width / 2, self.y - self.height / 2,
                        self.x + self.width / 4, self.y + self.height / 4 - 10)
            else:
                return (self.x - self.width / 4, self.y - self.height / 2,
                        self.x + self.width / 2, self.y + self.height / 4 - 10)

    def draw_collision_box(self):
        """충돌 박스 그리기 (디버그용)"""
        if SKRR.SKRR.show_collision_box:
            from pico2d import draw_rectangle
            if game_world.camera:
                camera_x, camera_y = game_world.camera.get_position()
                left, bottom, right, top = self.get_bb()
                draw_rectangle(left - camera_x, bottom - camera_y,
                             right - camera_x, top - camera_y)

                hit_left, hit_bottom, hit_right, hit_top = self.get_hit_bb()
                draw_rectangle(hit_left - camera_x, hit_bottom - camera_y,
                             hit_right - camera_x, hit_top - camera_y)

    def update(self):
        if not self.is_alive:
            return

        self.apply_gravity()
        self.check_tile_collision()

        player = SKRR.get_player()
        if player:
            self.dis_to_player = abs(self.x - player.x)

            # 태클 중, 공격 중이 아닐 때만 방향 전환
            if not self.is_tackling and not self.is_attacking and not self.is_tackle_ready and not self.is_tackle_end:
                if player.x > self.x:
                    self.face_dir = 1
                else:
                    self.face_dir = -1

            current_time = get_time()
            detect_range = 500

            # 태클 준비 중 - 범위와 관계없이 완료
            if self.is_tackle_ready:
                self.state = 'TACKLE_READY'
                self.tackle_ready_timer += game_framework.frame_time

                if self.tackle_ready_timer >= self.tackle_ready_duration:
                    self.is_tackle_ready = False
                    self.is_tackling = True
                    self.tackle_ready_timer = 0
                    self.tackle_traveled = 0
                    self.state = 'TACKLE'

            # 태클 실행 중 - 범위와 관계없이 완료
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

            # 태클 종료 중 - 범위와 관계없이 완료
            elif self.is_tackle_end:
                self.state = 'TACKLE_END'
                self.tackle_end_timer += game_framework.frame_time

                if self.tackle_end_timer >= self.tackle_end_duration:
                    self.is_tackle_end = False
                    self.tackle_end_timer = 0
                    self.tackle_last_use_time = current_time
                    self.state = 'IDLE'

            # 공격 중 - 범위와 관계없이 완료
            elif self.is_attacking:
                self.state = 'ATTACK'

            # 감지 범위 내에서만 새로운 행동 시작
            elif self.dis_to_player <= detect_range:
                # 새로운 태클 시작
                if current_time - self.tackle_last_use_time >= self.tackle_cooldown_time:
                    self.is_tackle_ready = True
                    self.tackle_ready_timer = 0
                    self.state = 'TACKLE_READY'
                else:
                    attack_range = 80
                    detect_range_normal = 400

                    if self.dis_to_player <= attack_range:
                        if current_time - self.attack_last_use_time >= self.attack_cooldown_time:
                            self.state = 'ATTACK'
                            self.is_attacking = True
                            self.attack_last_use_time = current_time
                        else:
                            self.state = 'IDLE'
                    elif self.dis_to_player <= detect_range_normal:
                        self.state = 'WALK'
                        self.x += self.velocity * self.face_dir * game_framework.frame_time
                    else:
                        self.state = 'IDLE'
            else:
                # 감지 범위 밖이면 IDLE
                self.state = 'IDLE'

        # 맵 경계 체크
        if self.tile_map:
            map_width_pixels = self.tile_map.map_width * self.tile_map.tile_width
            if self.x < self.width / 2:
                self.x = self.width / 2
            elif self.x > map_width_pixels - self.width / 2:
                self.x = map_width_pixels - self.width / 2

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

        self.draw_collision_box()
