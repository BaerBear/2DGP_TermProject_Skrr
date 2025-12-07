from pico2d import *
from ResourceManager import ResourceManager
import SKRR
import random
import game_framework
import game_world
from Sound_Loader import SoundManager
from Gold import Gold

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

    HIT_TIME_PER_ACTION = 0.15
    HIT_ACTION_PER_TIME = 1.0 / HIT_TIME_PER_ACTION
    HIT_FRAMES_PER_ACTION = 2

    def __init__(self, x, y):
        self.type = None
        self.x, self.y = x, y
        self.frame = 0
        self.frame_time = 0
        self.face_dir = -1 if random.randint(-100, 100) < 0 else 1
        self.scale = 2
        self.is_alive = True

        # 임의 스탯
        self.max_hp = 100
        self.current_hp = self.max_hp
        self.attack_power = 15
        self.defense = 3

        # 공격 판정
        self.active_hitbox = None
        self.attack_bounding_box = None
        self.hit_targets = set()
        self.hit_timestamps = {}  # 각 타겟을 마지막으로 타격한 시간 기록

        self.velocity = ENEMY_WALK_SPEED_PPS
        self.dis_to_player = 0

        self.is_attacking = False
        self.is_hit = False
        self.hit_duration = 0.3  # hit 상태 지속 시간
        self.hit_timer = 0
        self.attack_cooldown_time = 2
        self.attack_last_use_time = get_time()
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

        # hit 상태 처리
        if self.is_hit:
            self.hit_timer += game_framework.frame_time
            if self.hit_timer >= self.hit_duration:
                self.is_hit = False
                self.hit_timer = 0
                self.state = 'IDLE'
            else:
                self.state = 'HIT'
                if self.state != self.prev_state:
                    self.frame_time = 0
                    self.prev_state = self.state
                self.frame_time += game_framework.frame_time
                self.frame = int(self.frame_time * self.HIT_ACTION_PER_TIME * self.HIT_FRAMES_PER_ACTION)
                self.check_tile_collision()
                return

        player = SKRR.get_player()
        if player:
            # 플레이어가 죽었으면 새로운 공격을 시작하지 않음
            if not player.is_alive():
                # 공격 중이면 완료될 때까지 계속 진행
                if self.is_attacking:
                    self.state = 'ATTACK'
                else:
                    # 공격 중이 아니면 IDLE 상태 유지
                    self.state = 'IDLE'
                    self.clear_attack_hitbox()

                    if self.state != self.prev_state:
                        self.frame_time = 0
                        self.prev_state = self.state

                    self.frame_time += game_framework.frame_time
                    self.frame = int(self.frame_time * self.IDLE_ACTION_PER_TIME * self.IDLE_FRAMES_PER_ACTION)
                    self.check_tile_collision()
                    return

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
            elif self.dis_to_player <= detect_range and player.y >= self.y - 200 and player.y <= self.y + 200:
                if self.dis_to_player <= attack_range:
                    if current_time - self.attack_last_use_time >= self.attack_cooldown_time:
                        if self.type == 'Knight_Sword':
                            SoundManager.play_enemy_sound('sword_attack')
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

    def take_damage(self, damage, attacker_x):
        if self.current_hp <= 0:
            return False

        actual_damage = int(damage * (100 / (100 + self.defense)))
        damage_variation = max(1, random.randint(actual_damage - int(actual_damage * 0.2),
                                          actual_damage + int(actual_damage * 0.2)))
        self.current_hp -= damage_variation
        print(f'Enemy took {damage_variation} damage, current HP: {self.current_hp}/{self.max_hp}')

        if self.current_hp <= 0:
            self.on_death()
            return True

        # 피격 시 hit 상태로 전환하고 쿨다운 타이머 리셋
        self.is_hit = True
        self.hit_timer = 0
        self.attack_last_use_time = get_time() # 공격 쿨다운 타이머 리셋
        self.state = 'HIT'
        self.clear_attack_hitbox()
        self.is_attacking = False

        return True

    def on_death(self):
        self.is_alive = False
        if self.type == 'Knight_Sword' or self.type == 'Knight_Bow':
            SoundManager.play_enemy_sound('enemy_dead')
        elif self.type == 'Knight_Tackle':
            SoundManager.play_enemy_sound('enemy_big_dead')
        else:
            pass

        # 골드 생성
        gold_amount = random.randint(8, 20)  # 적마다 랜덤 골드량
        gold = Gold(self.x, self.y, gold_amount)
        gold.set_tile_map(self.tile_map)  # 타일맵 정보 전달
        game_world.add_object(gold, 1)  # 레이어 1에 추가

        game_world.remove_object(self)
        pass

    def handle_collision(self, group, other):
        if group == 'player_attack:enemy':
            pass

    def draw_collision_box(self):
        """충돌 박스 그리기 (디버그용)"""
        if game_framework.show_collision_boxes:
            from pico2d import draw_rectangle
            if game_world.camera:
                camera_x, camera_y = game_world.camera.get_position()
                left, bottom, right, top = self.get_bb()
                draw_rectangle(left - camera_x, bottom - camera_y,
                             right - camera_x, top - camera_y)

                # 공격 히트박스도 그리기
                hitbox = self.attack_bounding_box
                if hitbox:
                    draw_rectangle(hitbox[0] - camera_x, hitbox[1] - camera_y,
                                   hitbox[2] - camera_x, hitbox[3] - camera_y)

    def set_attack_hitbox(self, width, height, center_offset_x=0, center_offset_y=0, damage=None, multi_hit=False, hit_interval=0.0):
        self.active_hitbox = {
            'width': width,
            'height': height,
            'center_offset_x': center_offset_x,
            'center_offset_y': center_offset_y,
            'damage': damage if damage else self.attack_power,
            'multi_hit': multi_hit,
            'hit_interval': hit_interval
        }
        if not multi_hit:
            self.hit_targets.clear()
            self.hit_timestamps.clear()
        else:
            self.hit_timestamps.clear()

    def update_attack_hitbox_position(self, center_offset_x, center_offset_y, width=None):
        if self.active_hitbox:
            self.active_hitbox['center_offset_x'] = center_offset_x
            self.active_hitbox['center_offset_y'] = center_offset_y
            if width is not None:
                self.active_hitbox['width'] = width

    def get_attack_hitbox(self):
        if self.active_hitbox is None:
            return None

        hitbox_center_x = self.x + (self.active_hitbox['center_offset_x'] * self.face_dir)
        hitbox_center_y = self.y + self.active_hitbox['center_offset_y']

        half_width = self.active_hitbox['width'] / 2
        half_height = self.active_hitbox['height'] / 2
        self.attack_bounding_box = (hitbox_center_x - half_width, hitbox_center_y - half_height,
                                    hitbox_center_x + half_width, hitbox_center_y + half_height)

        return (hitbox_center_x - half_width, hitbox_center_y - half_height,
                hitbox_center_x + half_width, hitbox_center_y + half_height)

    def clear_attack_hitbox(self):
        self.active_hitbox = None
        self.attack_bounding_box = None
        self.hit_targets.clear()
        self.hit_timestamps.clear()

    def can_hit_target(self, target):
        if not self.active_hitbox:
            return False

        is_multi_hit = self.active_hitbox.get('multi_hit', False)
        hit_interval = self.active_hitbox.get('hit_interval', 0.0)

        if not is_multi_hit:
            return target not in self.hit_targets

        if hit_interval == 0.0:
            return True

        if target not in self.hit_timestamps:
            return True

        current_time = get_time()
        last_hit_time = self.hit_timestamps[target]
        return (current_time - last_hit_time) >= hit_interval

    def add_hit_target(self, target):
        self.hit_targets.add(target)
        if self.active_hitbox and self.active_hitbox.get('multi_hit', False):
            self.hit_timestamps[target] = get_time()

class Knight_Sword(Enemy):
    images = None

    def __init__(self, x, y):
        super().__init__(x, y)
        self.type = 'Knight_Sword'
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

        player = SKRR.get_player()
        if player and not player.is_alive():
            if self.is_attacking and self.state == 'ATTACK':
                self._handle_attack_frames()
            return

        if self.state == 'ATTACK':
            self._handle_attack_frames()

    def _handle_attack_frames(self):
        if not self.active_hitbox and self.frame == 10:
            self.set_attack_hitbox(
                width=80,
                height=self.height * 0.8,
                center_offset_x=40,
                center_offset_y=0,
                damage=self.attack_power,
                multi_hit=False
            )
        elif self.frame == 15:
            self.clear_attack_hitbox()

        attack_duration = len(Knight_Sword.images.get('attack', [])) * self.ATTACK_TIME_PER_ACTION
        if self.frame_time >= attack_duration:
            self.is_attacking = False
            self.clear_attack_hitbox()

    def draw(self):
        if not self.is_alive:
            if 'dead' in Knight_Sword.images and Knight_Sword.images['dead']:
                img = Knight_Sword.images['dead'][int(self.frame_time * self.ATTACK_ACTION_PER_TIME) % len(Knight_Sword.images['dead'])]
            else:
                return
        elif self.state == 'HIT':
            if 'hit' in Knight_Sword.images and Knight_Sword.images['hit']:
                img = Knight_Sword.images['hit'][int(self.frame_time * self.HIT_ACTION_PER_TIME) % len(Knight_Sword.images['hit'])]
            else:
                if 'idle' in Knight_Sword.images and Knight_Sword.images['idle']:
                    img = Knight_Sword.images['idle'][0]
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
        self.type = 'Knight_Bow'
        self.max_hp = 80
        self.current_hp = self.max_hp
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

    def take_damage(self, damage, attacker_x):
        if self.current_hp <= 0:
            return False

        actual_damage = int(damage * (100 / (100 + self.defense)))
        damage_variation = max(1, random.randint(actual_damage - int(actual_damage * 0.2),
                                          actual_damage + int(actual_damage * 0.2)))
        self.current_hp -= damage_variation
        print(f'Knight_Bow took {damage_variation} damage, current HP: {self.current_hp}/{self.max_hp}')

        if self.current_hp <= 0:
            self.on_death()
            return True

        self.is_hit = True
        self.hit_timer = 0
        self.attack_last_use_time = get_time()
        self.clear_attack_hitbox()
        self.is_attacking = False
        self.state = 'HIT'

        # 조준 취소
        if self.is_aiming:
            self.is_aiming = False
            self.aim_timer = get_time()
            self.sign_frame = 0
            self.state = 'HIT'

        return True

    def update(self):
        if not self.is_alive:
            return

        self.apply_gravity()
        self.check_tile_collision()

        # hit 상태 처리
        if self.is_hit:
            self.hit_timer += game_framework.frame_time
            if self.hit_timer >= self.hit_duration:
                self.is_hit = False
                self.hit_timer = 0
                self.state = 'IDLE'
            else:
                self.state = 'HIT'
                if self.state != self.prev_state:
                    self.frame_time = 0
                    self.prev_state = self.state
                self.frame_time += game_framework.frame_time
                self.frame = int(self.frame_time * self.HIT_ACTION_PER_TIME * self.HIT_FRAMES_PER_ACTION)
                self.check_tile_collision()
                return

        player = SKRR.get_player()
        if player:
            if not player.is_alive():
                if self.is_aiming or self.is_attacking:
                    self._handle_bow_attack()
                    return
                else:
                    self._handle_idle()
                    return

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
                self._handle_aiming(current_time)
            elif current_time - self.attack_last_use_time >= self.attack_cooldown_time and not self.is_attacking:
                if self.dis_to_player <= detect_range and player.y >= self.y - 200 and player.y <= self.y + 200:
                    SoundManager.play_enemy_sound('arrow_ready')
                    self.is_aiming = True
                    self.aim_timer = 0
                    self.state = 'AIM'
                    self.sign_frame = 0
            elif not self.is_attacking and not self.is_aiming:
                self._handle_movement(attack_range_min, attack_range_max, detect_range)

        self._update_frame_time()

    def _handle_bow_attack(self):
        if self.is_aiming:
            self.state = 'AIM'
            self.aim_timer += game_framework.frame_time
            if self.aim_timer >= self.aim_duration:
                self.state = 'ATTACK'
                self.is_aiming = False
                self.is_attacking = True
                self.aim_timer = 0
                self.attack_last_use_time = get_time()

        if self.is_attacking and self.state == 'ATTACK':
            if not self.active_hitbox:
                sign_img = Knight_Bow.images['attack_sign'][0]
                w = sign_img.w * self.scale
                h = sign_img.h / 4
                self.set_attack_hitbox(
                    width=w,
                    height=h,
                    center_offset_x=w / 2,
                    damage=self.attack_power,
                    multi_hit=False
                )
                SoundManager.play_enemy_sound('arrow_fire')

            self.frame = 3
            attack_duration = len(Knight_Bow.images.get('attack', [])) * self.ATTACK_TIME_PER_ACTION
            self.sign_frame = int(self.frame_time * self.SIGN_ACTION_PER_TIME * self.SIGN_FRAMES_PER_ACTION) % len(Knight_Bow.images['attack_sign'])

            if self.frame_time < 0.2:
                self.get_attack_hitbox()
            else:
                self.attack_bounding_box = None

            if self.frame_time >= attack_duration:
                self.is_attacking = False
                self.clear_attack_hitbox()

    def _handle_idle(self):
        self.state = 'IDLE'
        self.clear_attack_hitbox()

        if self.state != self.prev_state:
            self.frame_time = 0
            self.prev_state = self.state

        self.frame_time += game_framework.frame_time
        self.frame = int(self.frame_time * self.IDLE_ACTION_PER_TIME * self.IDLE_FRAMES_PER_ACTION)

    def _handle_aiming(self, current_time):
        self.state = 'AIM'
        self.aim_timer += game_framework.frame_time
        if self.aim_timer >= self.aim_duration:
            self.state = 'ATTACK'
            self.is_aiming = False
            self.is_attacking = True
            self.aim_timer = 0
            self.attack_last_use_time = current_time

    def _handle_movement(self, attack_range_min, attack_range_max, detect_range):
        if self.dis_to_player < attack_range_min:
            self.state = 'WALK'
            self.x -= self.velocity * self.face_dir * game_framework.frame_time
        elif self.dis_to_player > attack_range_max and self.dis_to_player <= detect_range:
            self.state = 'WALK'
            self.x += self.velocity * self.face_dir * game_framework.frame_time
        else:
            self.state = 'IDLE'

    def _update_frame_time(self):
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
            self.sign_frame = int(self.frame_time * self.SIGN_ACTION_PER_TIME * self.SIGN_FRAMES_PER_ACTION) % len(Knight_Bow.images['attack_sign'])
        elif self.state == 'ATTACK':
            if not self.active_hitbox:
                sign_img = Knight_Bow.images['attack_sign'][0]
                w = sign_img.w * self.scale
                h = sign_img.h / 4
                self.set_attack_hitbox(
                    width=w,
                    height=h,
                    center_offset_x=w / 2,
                    damage=self.attack_power,
                    multi_hit=False
                )
                SoundManager.play_enemy_sound('arrow_fire')

            self.frame = 3
            attack_duration = len(Knight_Bow.images.get('attack', [])) * self.ATTACK_TIME_PER_ACTION
            self.sign_frame = int(self.frame_time * self.SIGN_ACTION_PER_TIME * self.SIGN_FRAMES_PER_ACTION)

            if self.frame_time < 0.2:
                self.get_attack_hitbox()
            else:
                self.attack_bounding_box = None

            if self.frame_time >= attack_duration:
                self.is_attacking = False
                self.clear_attack_hitbox()

    def draw(self):
        if not self.is_alive:
            if 'dead' in Knight_Bow.images and Knight_Bow.images['dead']:
                img = Knight_Bow.images['dead'][int(self.frame_time * self.ATTACK_ACTION_PER_TIME) % len(Knight_Bow.images['dead'])]
            else:
                return
        elif self.state == 'HIT':
            if 'hit' in Knight_Bow.images and Knight_Bow.images['hit']:
                img = Knight_Bow.images['hit'][int(self.frame_time * self.HIT_ACTION_PER_TIME) % len(Knight_Bow.images['hit'])]
            else:
                if 'idle' in Knight_Bow.images and Knight_Bow.images['idle']:
                    img = Knight_Bow.images['idle'][0]
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
        self.type = 'Knight_Tackle'
        self.max_hp = 150
        self.current_hp = self.max_hp
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

    def take_damage(self, damage, attacker_x):
        if self.current_hp <= 0:
            return False

        actual_damage = int(damage * (100 / (100 + self.defense)))
        damage_variation = max(1, random.randint(actual_damage - int(actual_damage * 0.2),
                                          actual_damage + int(actual_damage * 0.2)))
        self.current_hp -= damage_variation
        print(f'Knight_Tackle took {damage_variation} damage, current HP: {self.current_hp}/{self.max_hp}')

        if self.current_hp <= 0:
            self.on_death()
            return True

        if self.is_tackling:
            return True

        self.is_hit = True
        self.hit_timer = 0
        self.clear_attack_hitbox()

        return True

    def update(self):
        if not self.is_alive:
            return

        self.apply_gravity()
        self.check_tile_collision()

        player = SKRR.get_player()
        if player:
            # 플레이어가 죽었을 때는 새로운 공격/태클을 시작하지 않음
            if not player.is_alive():
                # 태클 중이거나 공격 중이면 완료될 때까지 계속 진행
                if self.is_tackle_ready or self.is_tackling or self.is_tackle_end or self.is_attacking:
                    # 태클 준비 중
                    if self.is_tackle_ready:
                        self.state = 'TACKLE_READY'
                        self.tackle_ready_timer += game_framework.frame_time

                        if self.tackle_ready_timer >= self.tackle_ready_duration:
                            self.is_tackle_ready = False
                            self.is_tackling = True
                            self.tackle_ready_timer = 0
                            self.tackle_traveled = 0
                            self.state = 'TACKLE'

                    # 태클 실행 중
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

                    # 태클 종료 중
                    elif self.is_tackle_end:
                        self.state = 'TACKLE_END'
                        self.tackle_end_timer += game_framework.frame_time

                        if self.tackle_end_timer >= self.tackle_end_duration:
                            self.is_tackle_end = False
                            self.tackle_end_timer = 0
                            self.tackle_last_use_time = get_time()
                            self.state = 'IDLE'

                    # 일반 공격 중
                    elif self.is_attacking:
                        self.state = 'ATTACK'
                        if not self.active_hitbox:
                            self.set_attack_hitbox(
                                width=100,
                                height=self.height * 0.8,
                                center_offset_x=self.width * 0.4,
                                center_offset_y=-20,
                                damage=self.attack_power,
                                multi_hit=False
                            )

                        self.frame = int(self.frame_time * self.ATTACK_ACTION_PER_TIME * self.ATTACK_FRAMES_PER_ACTION)

                        if 2 <= self.frame < 6:
                            self.get_attack_hitbox()

                        attack_duration = len(Knight_Tackle.images.get('attack', [])) * self.ATTACK_TIME_PER_ACTION
                        if self.frame_time >= attack_duration:
                            self.is_attacking = False
                            self.clear_attack_hitbox()

                    # 프레임 업데이트
                    if self.state != self.prev_state:
                        self.frame_time = 0
                        self.prev_state = self.state

                    self.frame_time += game_framework.frame_time

                    # 상태별 프레임 계산
                    if self.state == 'TACKLE_READY':
                        self.frame = 0
                    elif self.state == 'TACKLE':
                        self.get_attack_hitbox()
                        self.frame = 1
                    elif self.state == 'TACKLE_END':
                        if self.tackle_end_timer < game_framework.frame_time:
                            self.clear_attack_hitbox()
                        self.frame = 2

                    return
                else:
                    # 공격/태클 중이 아니면 IDLE 상태 유지
                    self.state = 'IDLE'
                    self.clear_attack_hitbox()

                    if self.state != self.prev_state:
                        self.frame_time = 0
                        self.prev_state = self.state

                    self.frame_time += game_framework.frame_time
                    self.frame = int(self.frame_time * self.IDLE_ACTION_PER_TIME * self.IDLE_FRAMES_PER_ACTION)
                    return

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
            elif self.dis_to_player <= detect_range and player.y >= self.y - 150 and player.y <= self.y + 150:
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
            # 일반 공격 히트박스 설정
            if not self.active_hitbox:  # 공격 시작 프레임
                self.set_attack_hitbox(
                    width=100,
                    height=self.height * 0.8,
                    center_offset_x=self.width * 0.4,
                    center_offset_y= -20,
                    damage=self.attack_power,
                    multi_hit=False
                )

            self.frame = int(self.frame_time * self.ATTACK_ACTION_PER_TIME * self.ATTACK_FRAMES_PER_ACTION)

            if 2 <= self.frame < 6:
                self.get_attack_hitbox()

            attack_duration = len(Knight_Tackle.images.get('attack', [])) * self.ATTACK_TIME_PER_ACTION
            if self.frame_time >= attack_duration:
                self.is_attacking = False
                self.clear_attack_hitbox()
        elif self.state == 'TACKLE_READY':
            self.frame = 0
        elif self.state == 'TACKLE':
            # 태클 시작 시 히트박스 설정
            if not self.active_hitbox:
                self.set_attack_hitbox(
                    width=self.width * 1.2,
                    height=self.height * 0.9,
                    center_offset_y= -40,
                    damage=int(self.attack_power * 1.5),
                    multi_hit=False
                )

            # 태클 중에는 계속 히트박스 활성화
            self.get_attack_hitbox()
            self.frame = 1
        elif self.state == 'TACKLE_END':
            if self.tackle_end_timer < game_framework.frame_time:
                self.clear_attack_hitbox()
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

        if self.is_tackling:
            effect_img = Knight_Tackle.images['tackle_effect'][int(self.frame_time * self.ATTACK_ACTION_PER_TIME) % len(Knight_Tackle.images['tackle_effect'])]
            if self.face_dir == 1:
                effect_img.clip_draw(0, 0, effect_img.w, effect_img.h, cam_x + self.width / 2, cam_y, effect_img.w * self.scale, effect_img.h * 4)
            else:
                effect_img.clip_composite_draw(0, 0, effect_img.w, effect_img.h, 0, 'h', cam_x - self.width / 2, cam_y - 30, effect_img.w * self.scale, effect_img.h * 4)

        self.draw_collision_box()
