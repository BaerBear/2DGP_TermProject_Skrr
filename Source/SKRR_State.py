from pico2d import get_canvas_width, get_time
from Sound_Loader import SoundManager
import game_framework

PIXEL_PER_METER = (10.0 / 0.3)
RUN_SPEED_KMPH = 20.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

GRAVITY_MULTIPLIER = 4.0
BASE_GRAVITY = 9.8
GRAVITY = BASE_GRAVITY * GRAVITY_MULTIPLIER

BASE_JUMP_POWER_PPS = 10.0
JUMP_POWER_PPS = BASE_JUMP_POWER_PPS * (GRAVITY_MULTIPLIER ** 0.5)

DASH_SPEED_PPS = 10 * 60

class Idle:
    TIME_PER_ACTION = 0.167
    ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
    FRAMES_PER_ACTION = 10

    def __init__(self, skrr):
        self.skrr = skrr
        self.timer = 0
        self.frame_time = 0

    def enter(self, e):
        self.skrr.frame = 0
        self.frame_time = 0
        self.skrr.is_grounded = True
        self.skrr.jump_count = 0
        self.timer = get_time()

    def do(self):
        self.frame_time += game_framework.frame_time
        self.skrr.frame = int(self.frame_time * self.ACTION_PER_TIME * self.FRAMES_PER_ACTION)

        if get_time() - self.timer > 4.0:
            self.skrr.state_machine.handle_event(('TIME_OUT', None))

    def exit(self, e):
        pass

    def draw(self):
        img = self.skrr.images['Idle'][int(self.frame_time * self.ACTION_PER_TIME) % len(self.skrr.images['Idle'])]
        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)


class Wait:
    TIME_PER_ACTION = 0.1
    ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
    FRAMES_PER_ACTION = 6

    def __init__(self, skrr):
        self.skrr = skrr
        self.frame_time = 0
        self.total_frames = 46 * 6

    def enter(self, e):
        self.skrr.frame = 0
        self.frame_time = 0

    def do(self):
        self.frame_time += game_framework.frame_time
        self.skrr.frame = int(self.frame_time * self.ACTION_PER_TIME * self.FRAMES_PER_ACTION)

        if self.skrr.frame >= self.total_frames:
            self.skrr.state_machine.handle_event(('ANIMATION_END', None))

    def exit(self, e):
        pass

    def draw(self):
        img = self.skrr.images['Wait'][int(self.frame_time * self.ACTION_PER_TIME) % len(self.skrr.images['Wait'])]
        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)


class Walk:
    TIME_PER_ACTION = 0.1
    ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
    FRAMES_PER_ACTION = 6

    def __init__(self, skrr):
        self.skrr = skrr
        self.frame_time = 0

    def enter(self, e):
        self.skrr.frame = 0
        self.frame_time = 0

    def do(self):
        minX = self.skrr.images['Walk'][0].w * self.skrr.scale // 2 - 10
        self.frame_time += game_framework.frame_time
        self.skrr.frame = int(self.frame_time * self.ACTION_PER_TIME * self.FRAMES_PER_ACTION)

        if not self.skrr.is_moving:
            self.skrr.state_machine.handle_event(('STOP_MOVING', None))
            return

        if self.skrr.x <= minX and self.skrr.face_dir == -1:
            self.skrr.x = minX
        elif self.skrr.x >= get_canvas_width() - minX and self.skrr.face_dir == 1:
            self.skrr.x = get_canvas_width() - minX
        else:
            self.skrr.x += self.skrr.face_dir * RUN_SPEED_PPS * game_framework.frame_time

    def exit(self, e):
        pass

    def draw(self):
        img = self.skrr.images['Walk'][int(self.frame_time * self.ACTION_PER_TIME) % len(self.skrr.images['Walk'])]
        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)


class Jump:
    TIME_PER_ACTION = 0.25
    ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
    FRAMES_PER_ACTION = 15

    EFFECT_TIME_PER_ACTION = 0.05
    EFFECT_ACTION_PER_TIME = 1.0 / EFFECT_TIME_PER_ACTION
    EFFECT_FRAMES_PER_ACTION = 3

    def __init__(self, skrr):
        self.skrr = skrr
        self.minX = 0
        self.effect_x = None
        self.effect_y = None
        self.effect_frame_time = 0
        self.frame_time = 0

    def enter(self, e):
        self.skrr.frame = 0
        self.frame_time = 0
        self.minX = self.skrr.images['Walk'][0].w * self.skrr.scale // 2 - 10
        self.skrr.jumping = True
        if self.skrr.jump_count == 0:
            self.skrr.jump_count = 1
            self.skrr.is_grounded = False
            self.skrr.velocity_y = JUMP_POWER_PPS
            SoundManager.play_player_sound('Jump')
        elif self.skrr.jump_count == 1:
            self.skrr.jump_count = 2
            self.skrr.velocity_y = JUMP_POWER_PPS
            self.effect_x = self.skrr.x
            self.effect_y = self.skrr.y
            self.effect_frame_time = 0
            SoundManager.play_player_sound('Jump_air')

    def do(self):
        self.frame_time += game_framework.frame_time
        self.skrr.frame = int(self.frame_time * self.ACTION_PER_TIME * self.FRAMES_PER_ACTION)

        if self.effect_y is not None:
            self.effect_frame_time += game_framework.frame_time

        self.skrr.y += self.skrr.velocity_y * game_framework.frame_time * PIXEL_PER_METER
        self.skrr.velocity_y -= GRAVITY * game_framework.frame_time

        if self.skrr.velocity_y < 0 and not self.skrr.is_grounded:
            self.skrr.state_machine.handle_event(('START_FALLING', None))
            return

        if self.skrr.is_moving:
            move_speed = RUN_SPEED_PPS * game_framework.frame_time
            new_x = self.skrr.x + self.skrr.face_dir * move_speed

            if self.minX <= new_x <= get_canvas_width() - self.minX:
                self.skrr.x = new_x

    def exit(self, e):
        self.effect_x = None
        self.effect_y = None
        self.effect_frame_time = 0

    def draw(self):
        img = self.skrr.images['Jump'][int(self.frame_time * self.ACTION_PER_TIME) % len(self.skrr.images['Jump'])]
        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)

        if self.effect_y is not None and self.effect_frame_time < 0.5:
            if self.skrr.images['JumpEffect']:
                effect_idx = int(self.effect_frame_time * self.EFFECT_ACTION_PER_TIME) % len(self.skrr.images['JumpEffect'])
                effect_img = self.skrr.images['JumpEffect'][effect_idx]
                effect_img.clip_draw(0, 0, effect_img.w, effect_img.h, self.effect_x, self.effect_y,
                                     effect_img.w * self.skrr.scale, effect_img.h * self.skrr.scale)


class JumpAttack:
    TIME_PER_ACTION = 0.133
    ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
    FRAMES_PER_ACTION = 8

    def __init__(self, skrr):
        self.skrr = skrr
        self.minX = 0
        self.frame_time = 0
        self.total_frames = 16

    def enter(self, e):
        self.skrr.frame = 0
        self.frame_time = 0
        self.skrr.jumpattack_last_use_time = get_time()
        self.minX = self.skrr.images['Walk'][0].w * self.skrr.scale // 2 - 10
        SoundManager.play_player_sound('Jump_attack')

    def do(self):
        self.frame_time += game_framework.frame_time
        self.skrr.frame = int(self.frame_time * self.ACTION_PER_TIME * self.FRAMES_PER_ACTION)

        self.skrr.y += self.skrr.velocity_y * game_framework.frame_time * PIXEL_PER_METER
        self.skrr.velocity_y -= GRAVITY * game_framework.frame_time

        if self.skrr.is_moving:
            move_speed = RUN_SPEED_PPS * game_framework.frame_time
            new_x = self.skrr.x + self.skrr.face_dir * move_speed

            if self.minX <= new_x <= get_canvas_width() - self.minX:
                self.skrr.x = new_x

        if self.skrr.frame >= self.total_frames:
            self.skrr.state_machine.handle_event(('ANIMATION_END', None))
        elif self.skrr.y <= self.skrr.ground_y:
            self.skrr.y = self.skrr.ground_y
            self.skrr.is_grounded = True
            self.skrr.state_machine.handle_event(('ANIMATION_END', None))

    def exit(self, e):
        pass

    def draw(self):
        img = self.skrr.images['JumpAttack'][int(self.frame_time * self.ACTION_PER_TIME) % len(self.skrr.images['JumpAttack'])]
        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)


class Attack:
    TIME_PER_ACTION = 0.1
    ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
    FRAMES_PER_ACTION = 6

    def __init__(self, skrr):
        self.skrr = skrr
        self.attack_dir = None
        self.frame_time = 0

    def enter(self, e):
        self.skrr.frame = 0
        self.frame_time = 0
        if self.skrr.attack_type == 'A':
            SoundManager.play_player_sound('Attack1')
        elif self.skrr.attack_type == 'B':
            SoundManager.play_player_sound('Attack2')
        self.attack_dir = self.skrr.face_dir

    def do(self):
        self.frame_time += game_framework.frame_time
        self.skrr.frame = int(self.frame_time * self.ACTION_PER_TIME * self.FRAMES_PER_ACTION)

        if self.skrr.attack_type == 'A' and self.skrr.frame >= 15 * 2:
            if self.skrr.key_pressed['left'] or self.skrr.key_pressed['right']:
                self.skrr.state_machine.handle_event(('ANIMATION_END', 'WALK'))
            else:
                self.skrr.state_machine.handle_event(('ANIMATION_END', 'IDLE'))
            self.skrr.attack_type = None
        elif self.skrr.attack_type == 'B' and self.skrr.frame >= 12 * 2:
            if self.skrr.key_pressed['left'] or self.skrr.key_pressed['right']:
                self.skrr.state_machine.handle_event(('ANIMATION_END', 'WALK'))
            else:
                self.skrr.state_machine.handle_event(('ANIMATION_END', 'IDLE'))
            self.skrr.attack_type = None

    def exit(self, e):
        pass

    def draw(self):
        if self.skrr.attack_type == 'A':
            img = self.skrr.images['AttackA'][int(self.frame_time * self.ACTION_PER_TIME) % len(self.skrr.images['AttackA'])]
        elif self.skrr.attack_type == 'B':
            img = self.skrr.images['AttackB'][int(self.frame_time * self.ACTION_PER_TIME) % len(self.skrr.images['AttackB'])]
        else:
            return

        if self.attack_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.attack_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)


class Dash:
    EFFECT_TIME_PER_ACTION = 0.05
    EFFECT_ACTION_PER_TIME = 1.0 / EFFECT_TIME_PER_ACTION
    EFFECT_FRAMES_PER_ACTION = 3

    def __init__(self, skrr):
        self.skrr = skrr
        self.minX = 0
        self.dash_distance = 0
        self.max_dash_distance = 175
        self.can_second_dash = False
        self.dash_dir = None
        self.is_air_dash = False

        self.effect_frame_time = 0
        self.effect_x, self.effect_y = None, None

    def enter(self, e):
        self.skrr.frame = 0
        if self.skrr.dash_type == 0:
            self.dash_distance = 0
            self.can_second_dash = False
        self.minX = self.skrr.images['Walk'][0].w * self.skrr.scale // 2 - 10
        self.dash_dir = self.skrr.face_dir
        self.is_air_dash = not self.skrr.is_grounded

        self.effect_x, self.effect_y = self.skrr.x, self.skrr.y - 10
        self.effect_frame_time = 0
        self.skrr.is_invincible = True

        SoundManager.play_player_sound('Dash')

    def do(self):
        self.effect_frame_time += game_framework.frame_time

        if self.dash_distance >= 30:
            self.can_second_dash = True

        dash_move = DASH_SPEED_PPS * game_framework.frame_time

        if (self.dash_distance < self.max_dash_distance
                and ((self.dash_dir == 1 and self.skrr.x < get_canvas_width() - self.minX)
                     or (self.dash_dir == -1 and self.skrr.x > self.minX))):
            self.skrr.x += self.dash_dir * dash_move
            self.dash_distance += dash_move
        else:
            if self.is_air_dash:
                self.skrr.state_machine.handle_event(('DASH_COMPLETE', 'FALL'))
            else:
                if self.skrr.is_moving:
                    self.skrr.state_machine.handle_event(('DASH_COMPLETE', 'WALK'))
                else:
                    self.skrr.state_machine.handle_event(('DASH_COMPLETE', 'IDLE'))

    def exit(self, e):
        self.skrr.is_invincible = False

        if self.skrr.dash_type == 0 or self.skrr.dash_type == 1:
            self.skrr.dash_last_use_time = get_time()
            self.skrr.dash_type = None
        self.dash_distance = 0
        self.is_air_dash = False
        self.effect_x, self.effect_y = None, None

        self.skrr.velocity_y = 0

        if self.skrr.key_pressed['left'] and not self.skrr.key_pressed['right']:
            self.skrr.face_dir = -1
        elif self.skrr.key_pressed['right'] and not self.skrr.key_pressed['left']:
            self.skrr.face_dir = 1

    def draw(self):
        if self.skrr.images['DashEffect']:
            effect_idx = int(self.effect_frame_time * self.EFFECT_ACTION_PER_TIME) % len(self.skrr.images['DashEffect'])
            effect_img = self.skrr.images['DashEffect'][effect_idx]
            if self.dash_dir == 1:
                effect_img.clip_draw(0, 0, effect_img.w, effect_img.h, self.effect_x, self.effect_y, effect_img.w, effect_img.h)
            elif self.dash_dir == -1:
                effect_img.clip_composite_draw(0, 0, effect_img.w, effect_img.h, 0, 'h', self.effect_x, self.effect_y, effect_img.w, effect_img.h)
        img = self.skrr.images['Dash'][0]
        if self.dash_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.dash_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)



class Fall:
    TIME_PER_ACTION = 0.25
    ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
    FRAMES_PER_ACTION = 15

    def __init__(self, skrr):
        self.skrr = skrr
        self.minX = 0
        self.frame_time = 0

    def enter(self, e):
        self.skrr.frame = 0
        self.frame_time = 0
        self.skrr.jumping = True
        self.minX = self.skrr.images['Walk'][0].w * self.skrr.scale // 2 - 10

    def do(self):
        self.frame_time += game_framework.frame_time
        self.skrr.frame = int(self.frame_time * self.ACTION_PER_TIME * self.FRAMES_PER_ACTION)

        self.skrr.velocity_y -= GRAVITY * game_framework.frame_time
        self.skrr.y += self.skrr.velocity_y * game_framework.frame_time * PIXEL_PER_METER
        if self.skrr.y <= self.skrr.ground_y:
            self.skrr.y = self.skrr.ground_y
            self.skrr.is_grounded = True
            if self.skrr.is_moving:
                self.skrr.state_machine.handle_event(('LAND_ON_GROUND', 'WALK'))
            else:
                self.skrr.state_machine.handle_event(('LAND_ON_GROUND', 'IDLE'))
            self.skrr.velocity_y = 0
            self.skrr.jumping = False
            self.skrr.jump_count = 0
            return

        if self.skrr.is_moving:
            move_speed = RUN_SPEED_PPS * game_framework.frame_time
            new_x = self.skrr.x + self.skrr.face_dir * move_speed

            if self.minX <= new_x <= get_canvas_width() - self.minX:
                self.skrr.x = new_x

    def exit(self, e):
        pass

    def draw(self):
        if not self.skrr.images['Fall']:
            return

        idx = int(self.frame_time * self.ACTION_PER_TIME) % len(self.skrr.images['Fall'])
        img = self.skrr.images['Fall'][idx]
        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale,
                          img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale,
                                    img.h * self.skrr.scale)


class Dead:
    TIME_PER_ACTION = 0.25
    ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
    FRAMES_PER_ACTION = 15

    def __init__(self, skrr):
        self.skrr = skrr
        self.frame_time = 0
        self.total_frames = 30 * 5

    def enter(self, e):
        self.skrr.frame = 0
        self.frame_time = 0

    def do(self):
        self.frame_time += game_framework.frame_time
        self.skrr.frame = int(self.frame_time * self.ACTION_PER_TIME * self.FRAMES_PER_ACTION)

        if self.skrr.frame >= self.total_frames:
            self.skrr.state_machine.handle_event(('ANIMATION_END', None))

    def exit(self, e):
        pass

    def draw(self):
        img = self.skrr.images['Dead'][int(self.frame_time * self.ACTION_PER_TIME) % len(self.skrr.images['Dead'])]
        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)


class Reborn:
    TIME_PER_ACTION = 0.1
    ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
    FRAMES_PER_ACTION = 6

    def __init__(self, skrr):
        self.skrr = skrr
        self.frame_time = 0
        self.total_frames = 78 * 2

    def enter(self, e):
        self.skrr.frame = 0
        self.frame_time = 0

    def do(self):
        self.frame_time += game_framework.frame_time
        self.skrr.frame = int(self.frame_time * self.ACTION_PER_TIME * self.FRAMES_PER_ACTION)

        if self.skrr.frame >= self.total_frames:
            self.skrr.state_machine.handle_event(('ANIMATION_END', None))

    def exit(self, e):
        self.face_dir = 1

    def draw(self):
        img = self.skrr.images['Reborn'][int(self.frame_time * self.ACTION_PER_TIME) % len(self.skrr.images['Reborn'])]
        img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)
