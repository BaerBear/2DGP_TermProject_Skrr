from pico2d import *
from ResourceManager import ResourceManager
from State_Machine import StateMachine
from SKRR_State import Idle, Wait, Walk, Jump, JumpAttack, Attack, Dash, Fall, Dead, Reborn, Skill1, Skill2, Skill3
from SKRR_State_Rules import Get_State_Rules
import random

stage_start_positions = {
        0: (100, 256),      # Stage0 시작 위치
        1: (100, 608),      # Stage1 시작 위치
        2: (100, 512)       # BossStage 시작 위치
    }

_player_instance = None

def set_player(player):
    global _player_instance
    _player_instance = player

def get_player():
    return _player_instance

class SKRR:
    images = None
    show_collision_box = True  # 충돌 박스 표시 여부 (클래스 변수)
    default_w = 0
    default_h = 0

    @classmethod
    def load_images(cls):
        if cls.images is None:
            cls.images = ResourceManager.get_player_images()
            cls.default_w = cls.images['Idle'][0].w
            cls.default_h = cls.images['Idle'][0].h

    def __init__(self):
        SKRR.load_images()

        self.x, self.y = stage_start_positions[0]
        self.frame = 0
        self.face_dir = 1
        self.scale = 2
        self.key_pressed = {'left': False, 'right': False}

        # 충돌 박스 크기
        self.width = 15 * self.scale
        self.height = 35 * self.scale

        # 물리 속성
        self.velocity_y = 0
        self.gravity = -1000
        self.tile_map = None

        # 대쉬관련
        self.dash_type = None
        self.dash_cooldown_time = 0.8  # 대쉬 쿨타임
        self.dash_last_use_time = 0
        self.attack_type = None

        # 점프관련
        self.jumping = False
        self.jump_count = 0
        self.jumpattack_cooldown_time = 0.4 # 점프공격 쿨타임
        self.jumpattack_last_use_time = 0
        self.is_grounded = False
        self.was_grounded = False  # 이전 프레임의 바닥 상태 추적
        self.is_moving = False
        self.ground_y = 300  # 더미 값

        # 스탯
        self.max_hp = 150
        self.current_hp = self.max_hp
        self.attack_power = 10
        self.defense = 10

        # 피격관련
        self.is_invincible = False
        self.invincible_duration = 1.0  # 무적 시간 우선 1초
        self.invincible_start_time = 0.0
        self.is_hit = False

        # 공격 관련
        self.active_hitbox = None
        self.attack_bounding_box = None
        self.hit_targets = set()
        self.hit_timestamps = {}  # 각 적을 마지막으로 타격한 시간 기록

        # 스킬 시스템
        self.skill_cooldowns = {
            # 'skill1': 5.0,   # 스킬1 쿨타임 (초)
            # 'skill2': 8.0,   # 스킬2 쿨타임 (초)
            # 'skill3': 12.0   # 스킬3 쿨타임 (초)
            'skill1': 1.0,  # 디버깅용
            'skill2': 1.0,  # 디버깅용
            'skill3': 1.0   # 디버깅용
        }
        self.skill_last_use_time = {
            'skill1': -5.0,
            'skill2': -8.0,
            'skill3': -12.0
        }

        # State
        self.IDLE = Idle(self)
        self.WAIT = Wait(self)
        self.WALK = Walk(self)
        self.JUMP = Jump(self)
        self.JUMPATTACK = JumpAttack(self)
        self.ATTACK = Attack(self)
        self.DASH = Dash(self)
        self.FALL = Fall(self)
        self.DEAD = Dead(self)
        self.REBORN = Reborn(self)

        # 스킬 State
        self.SKILL1 = Skill1(self)
        self.SKILL2 = Skill2(self)
        self.SKILL3 = Skill3(self)

        self.state_machine = StateMachine(self.IDLE, Get_State_Rules(self))
        set_player(self)

    def set_tile_map(self, tile_map):
        self.tile_map = tile_map

    def update(self):
        self.was_grounded = self.is_grounded

        self.state_machine.update()

        if (not self.is_grounded and self.state_machine.current_state != self.DASH
                and (self.state_machine.current_state != self.SKILL3 and not self.is_grounded)):
            import game_framework
            self.velocity_y += self.gravity * game_framework.frame_time
            self.y += self.velocity_y * game_framework.frame_time

        if self.tile_map:
            self.check_tile_collision()

        if self.is_invincible:
            if get_time() - self.invincible_start_time >= self.invincible_duration:
                self.is_invincible = False

    # 피격
    def get_damage(self, damage):
        if self.is_invincible or self.state_machine.current_state == self.DEAD:
            return

        actual_damage = int(damage * (100 / (100 + self.defense)))
        self.current_hp -= random.randint(actual_damage - int(actual_damage * 0.1),
                                          actual_damage + int(actual_damage * 0.1))

        if self.current_hp <= 0:
            self.current_hp = 0
            self.state_machine.handle_event(('DEATH', None))

        self.is_invincible = True
        self.invincible_start_time = get_time()

    # 공격 히트박스 설정
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

    def update_skill3_bb(self, center_offset_x, center_offset_y, width=None):
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

    # 공격 히트박스 초기화
    def clear_attack_hitbox(self):
        self.active_hitbox = None
        self.attack_bounding_box = None
        self.hit_targets.clear()
        self.hit_timestamps.clear()

    # 중복 타격 방지
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

    def heal(self, amount):
        self.current_hp = min(self.max_hp, self.current_hp + amount)

    def is_alive(self):
        return self.current_hp > 0

    def check_tile_collision(self):
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
            self.jump_count = 0
        if (self.state_machine.current_state == self.IDLE or
            self.state_machine.current_state == self.WALK):
            if self.velocity_y < -1:
                self.state_machine.handle_event(('START_FALLING', None))

    def handle_tile_collision(self, tile):
        left, bottom, right, top = self.get_bb()

        overlap_left = right - tile['left']
        overlap_right = tile['right'] - left
        overlap_top = tile['top'] - bottom
        overlap_bottom = top - tile['bottom']

        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

        if min_overlap == overlap_bottom and self.velocity_y > 0:
            horizontal_overlap = min(overlap_left, overlap_right)
            if horizontal_overlap > self.width * 0.5:
                self.y = tile['bottom'] - self.height / 2
                self.velocity_y = 0
                return False
        elif min_overlap == overlap_top and self.velocity_y <= 0:
            self.y = tile['top'] + self.height / 2
            self.velocity_y = 0
            return True
        elif min_overlap == overlap_left:
            self.x = tile['left'] - self.width / 2
            return False
        elif min_overlap == overlap_right:
            self.x = tile['right'] + self.width / 2
            return False

        return False

    def handle_platform_collision(self, tile):
        left, bottom, right, top = self.get_bb()

        if self.velocity_y <= 0 and bottom <= tile['top'] and bottom >= tile['top'] - 10:
            if (self.state_machine.current_state == self.JUMP):
                if self.is_moving:
                    self.state_machine.handle_event(('LAND_ON_GROUND', 'WALK'))
                else:
                    self.state_machine.handle_event(('LAND_ON_GROUND', 'IDLE'))
            self.y = tile['top'] + self.height / 2
            self.velocity_y = 0
            return True

        return False

    def get_bb(self):
        return (self.x - self.width / 2, self.y - self.height / 2,
                self.x + self.width / 2, self.y + self.height / 2)

    def handle_collision(self, group, other):
        if group == 'player:tilemap':
            pass

    def is_dash_ready(self):
        return get_time() - self.dash_last_use_time >= self.dash_cooldown_time

    def is_jumpattack_ready(self):
        return get_time() - self.jumpattack_last_use_time >= self.jumpattack_cooldown_time

    def is_skill_ready(self, skill_name): # 쿨타임 체크
        return get_time() - self.skill_last_use_time[skill_name] >= self.skill_cooldowns[skill_name]

    def use_skill(self, skill_name): # 스킬 사용
        self.skill_last_use_time[skill_name] = get_time()

    def get_skill_cooldown_remaining(self, skill_name): # 남은 쿨타임 반환 (UI에 쓰기)
        elapsed = get_time() - self.skill_last_use_time[skill_name]
        remaining = self.skill_cooldowns[skill_name] - elapsed
        return max(0, remaining)

    def draw(self):
        self.state_machine.draw()
        if SKRR.show_collision_box:
            from pico2d import draw_rectangle
            from Camera import Camera
            camera = Camera.get_instance()
            if camera:
                camera_x, camera_y = camera.get_position()
                left, bottom, right, top = self.get_bb()
                draw_rectangle(left - camera_x, bottom - camera_y,
                              right - camera_x, top - camera_y)

                hitbox = self.attack_bounding_box
                if hitbox:
                    draw_rectangle(hitbox[0] - camera_x, hitbox[1] - camera_y,
                                   hitbox[2] - camera_x, hitbox[3] - camera_y)

    def handle_event(self, event):
        self.state_machine.handle_event(event)