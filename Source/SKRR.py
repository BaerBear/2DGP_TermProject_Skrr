from pico2d import *
from ResourceManager import ResourceManager
from State_Machine import StateMachine
from SKRR_State import Idle, Wait, Walk, Jump, JumpAttack, Attack, Dash, Fall, Dead, Reborn, Skill1, Skill2, Skill3
from SKRR_State_Rules import Get_State_Rules

_player_instance = None

def set_player(player):
    global _player_instance
    _player_instance = player

def get_player():
    return _player_instance

class SKRR:
    images = None

    @classmethod
    def load_images(cls):
        if cls.images is None:
            cls.images = ResourceManager.get_player_images()

    def __init__(self):
        SKRR.load_images()

        self.x, self.y = 100, get_canvas_height() // 2
        self.frame = 0
        self.face_dir = 1
        self.scale = 2
        self.key_pressed = {'left': False, 'right': False}

        # 대쉬관련
        self.dash_type = None
        self.dash_cooldown_time = 0.8  # 대쉬 쿨타임
        self.dash_last_use_time = 0
        self.attack_type = None

        # 점프관련
        self.jumping = False
        self.jump_count = 0
        self.jumpattack_cooldown_time = 0.5 # 점프공격 쿨타임
        self.jumpattack_last_use_time = 0
        self.is_grounded = True
        self.is_moving = False
        self.ground_y = get_canvas_height() // 2
        self.is_invincible = False

        # 스킬 시스템
        self.skill_cooldowns = {
            'skill1': 5.0,   # 스킬1 쿨타임 (초)
            'skill2': 8.0,   # 스킬2 쿨타임 (초)
            'skill3': 12.0   # 스킬3 쿨타임 (초)
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

    def update(self):
        self.state_machine.update()

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

    def handle_event(self, event):
        self.state_machine.handle_event(event)