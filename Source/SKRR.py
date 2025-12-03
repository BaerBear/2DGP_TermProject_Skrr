from pico2d import *
from ResourceManager import ResourceManager
from State_Machine import StateMachine
from SKRR_State import Idle, Wait, Walk, Jump, JumpAttack, Attack, Dash, Fall, Dead, Reborn, Skill1, Skill2, Skill3
from SKRR_State_Rules import Get_State_Rules

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

    @classmethod
    def load_images(cls):
        if cls.images is None:
            cls.images = ResourceManager.get_player_images()

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

        # 피격관련
        self.is_invincible = False
        self.invincibility_duration = 1.0  # 무적 시간 우선 1초
        self.invincibility_start_time = 0.0
        self.is_hit = False

        # 공격 관련
        self.active_hitbox = None
        self.hit_targets = set()

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

    def handle_event(self, event):
        self.state_machine.handle_event(event)