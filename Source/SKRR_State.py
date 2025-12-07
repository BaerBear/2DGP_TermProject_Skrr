from pico2d import get_canvas_width, get_time
from Sound_Loader import SoundManager
import game_framework
import game_world

PIXEL_PER_METER = (10.0 / 0.3)
RUN_SPEED_KMPH = 30.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

GRAVITY_MULTIPLIER = 5.0
BASE_GRAVITY = 9.8
GRAVITY = BASE_GRAVITY * GRAVITY_MULTIPLIER

BASE_JUMP_POWER_PPS = 10.0
JUMP_POWER_PPS = BASE_JUMP_POWER_PPS * (GRAVITY_MULTIPLIER ** 0.5)

DASH_SPEED_PPS = 10 * 50


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
        self.timer = get_time()

    def do(self):
        self.frame_time += game_framework.frame_time
        self.skrr.frame = int(self.frame_time * self.ACTION_PER_TIME * self.FRAMES_PER_ACTION)

        # 타임아웃 체크는 바닥에 있을 때만
        if self.skrr.is_grounded and get_time() - self.timer > 4.0:
            self.skrr.state_machine.handle_event(('TIME_OUT', None))

    def exit(self, e):
        pass

    def draw(self):
        img = self.skrr.images['Idle'][int(self.frame_time * self.ACTION_PER_TIME) % len(self.skrr.images['Idle'])]
        cam_x, cam_y = self.skrr.x, self.skrr.y
        if game_world.camera:
            cam_x, cam_y = game_world.camera.apply(self.skrr.x, self.skrr.y)

        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, cam_x, cam_y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', cam_x, cam_y, img.w * self.skrr.scale, img.h * self.skrr.scale)


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
        cam_x, cam_y = self.skrr.x, self.skrr.y
        if game_world.camera:
            cam_x, cam_y = game_world.camera.apply(self.skrr.x, self.skrr.y)

        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, cam_x, cam_y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', cam_x, cam_y, img.w * self.skrr.scale, img.h * self.skrr.scale)


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
        minX = self.skrr.images['Walk'][0].w * self.skrr.scale // 2 - 20
        self.frame_time += game_framework.frame_time
        self.skrr.frame = int(self.frame_time * self.ACTION_PER_TIME * self.FRAMES_PER_ACTION)

        if not self.skrr.is_moving:
            self.skrr.state_machine.handle_event(('STOP_MOVING', None))
            return

        # 타일맵 경계 체크
        if self.skrr.tile_map:
            max_x = self.skrr.tile_map.map_width * self.skrr.tile_map.tile_width
            min_x = max(0, minX)

            if self.skrr.x <= min_x and self.skrr.face_dir == -1:
                self.skrr.x = min_x
            elif self.skrr.x >= max_x - minX and self.skrr.face_dir == 1:
                self.skrr.x = max_x - minX
            else:
                new_x = self.skrr.x + self.skrr.face_dir * RUN_SPEED_PPS * game_framework.frame_time
                self.skrr.x = max(min_x, min(new_x, max_x - minX))
        else:
            min_x = max(0, minX)
            if self.skrr.x <= min_x and self.skrr.face_dir == -1:
                self.skrr.x = min_x
            elif self.skrr.x >= get_canvas_width() - minX and self.skrr.face_dir == 1:
                self.skrr.x = get_canvas_width() - minX
            else:
                new_x = self.skrr.x + self.skrr.face_dir * RUN_SPEED_PPS * game_framework.frame_time
                self.skrr.x = max(min_x, min(new_x, get_canvas_width() - minX))

    def exit(self, e):
        pass

    def draw(self):
        img = self.skrr.images['Walk'][int(self.frame_time * self.ACTION_PER_TIME) % len(self.skrr.images['Walk'])]
        cam_x, cam_y = self.skrr.x, self.skrr.y
        if game_world.camera:
            cam_x, cam_y = game_world.camera.apply(self.skrr.x, self.skrr.y)

        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, cam_x, cam_y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', cam_x, cam_y, img.w * self.skrr.scale, img.h * self.skrr.scale)


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
        self.minX = self.skrr.images['Walk'][0].w * self.skrr.scale // 2 - 20
        self.skrr.jumping = True
        if self.skrr.jump_count == 0:
            self.skrr.jump_count = 1
            self.skrr.is_grounded = False
            self.skrr.velocity_y = 500
            SoundManager.play_player_sound('Jump')
        elif self.skrr.jump_count == 1:
            self.skrr.jump_count = 2
            self.skrr.velocity_y = 500
            self.effect_x = self.skrr.x
            self.effect_y = self.skrr.y
            self.effect_frame_time = 0
            SoundManager.play_player_sound('Jump_air')

    def do(self):
        self.frame_time += game_framework.frame_time
        self.skrr.frame = int(self.frame_time * self.ACTION_PER_TIME * self.FRAMES_PER_ACTION)

        if self.effect_y is not None:
            self.effect_frame_time += game_framework.frame_time


        if self.skrr.velocity_y < 0 and not self.skrr.is_grounded:
            self.skrr.state_machine.handle_event(('START_FALLING', None))
            return

        if self.skrr.is_moving:
            move_speed = RUN_SPEED_PPS * game_framework.frame_time
            new_x = self.skrr.x + self.skrr.face_dir * move_speed

            # 타일맵 경계 체크
            if self.skrr.tile_map:
                max_x = self.skrr.tile_map.map_width * self.skrr.tile_map.tile_width
                min_x = max(0, self.minX)
                if min_x <= new_x <= max_x - self.minX:
                    self.skrr.x = new_x
                else:
                    self.skrr.x = max(min_x, min(new_x, max_x - self.minX))
            else:
                min_x = max(0, self.minX)
                if min_x <= new_x <= get_canvas_width() - self.minX:
                    self.skrr.x = new_x
                else:
                    self.skrr.x = max(min_x, min(new_x, get_canvas_width() - self.minX))

    def exit(self, e):
        self.effect_x = None
        self.effect_y = None
        self.effect_frame_time = 0

    def draw(self):
        img = self.skrr.images['Jump'][int(self.frame_time * self.ACTION_PER_TIME) % len(self.skrr.images['Jump'])]
        cam_x, cam_y = self.skrr.x, self.skrr.y
        if game_world.camera:
            cam_x, cam_y = game_world.camera.apply(self.skrr.x, self.skrr.y)

        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, cam_x, cam_y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', cam_x, cam_y, img.w * self.skrr.scale, img.h * self.skrr.scale)

        if self.effect_y is not None and self.effect_frame_time < 0.5:
            if self.skrr.images['JumpEffect']:
                effect_idx = int(self.effect_frame_time * self.EFFECT_ACTION_PER_TIME) % len(self.skrr.images['JumpEffect'])
                effect_img = self.skrr.images['JumpEffect'][effect_idx]
                effect_cam_x, effect_cam_y = self.effect_x, self.effect_y
                if game_world.camera:
                    effect_cam_x, effect_cam_y = game_world.camera.apply(self.effect_x, self.effect_y)
                effect_img.clip_draw(0, 0, effect_img.w, effect_img.h, effect_cam_x, effect_cam_y,
                                     effect_img.w * self.skrr.scale, effect_img.h * self.skrr.scale)


class JumpAttack:
    TIME_PER_ACTION = 0.1
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
        self.minX = self.skrr.images['Walk'][0].w * self.skrr.scale // 2 - 20
        SoundManager.play_player_sound('Jump_attack')

        self.skrr.set_attack_hitbox(
            width=70, height=self.skrr.default_h * self.skrr.scale + 40,
            center_offset_x= self.skrr.default_w // 2,
            damage = self.skrr.attack_power,
            multi_hit=False
        )

    def do(self):
        self.frame_time += game_framework.frame_time
        self.skrr.frame = int(self.frame_time * self.ACTION_PER_TIME * self.FRAMES_PER_ACTION)

        if self.skrr.is_moving:
            move_speed = RUN_SPEED_PPS * game_framework.frame_time
            new_x = self.skrr.x + self.skrr.face_dir * move_speed

            # 타일맵 경계 체크
            if self.skrr.tile_map:
                max_x = self.skrr.tile_map.map_width * self.skrr.tile_map.tile_width
                min_x = max(0, self.minX)
                if min_x <= new_x <= max_x - self.minX:
                    self.skrr.x = new_x
                else:
                    self.skrr.x = max(min_x, min(new_x, max_x - self.minX))
            else:
                min_x = max(0, self.minX)
                if min_x <= new_x <= get_canvas_width() - self.minX:
                    self.skrr.x = new_x
                else:
                    self.skrr.x = max(min_x, min(new_x, get_canvas_width() - self.minX))

        if self.skrr.frame >= self.total_frames:
            self.skrr.state_machine.handle_event(('ANIMATION_END', None))
        elif self.skrr.y <= self.skrr.ground_y:
            self.skrr.y = self.skrr.ground_y
            self.skrr.is_grounded = True
            self.skrr.state_machine.handle_event(('ANIMATION_END', None))

        if 2 <= self.skrr.frame < 6 or 10 <= self.skrr.frame < 14:
            self.skrr.get_attack_hitbox()
    def exit(self, e):
        self.skrr.clear_attack_hitbox()
        pass

    def draw(self):
        img = self.skrr.images['JumpAttack'][int(self.frame_time * self.ACTION_PER_TIME) % len(self.skrr.images['JumpAttack'])]
        cam_x, cam_y = self.skrr.x, self.skrr.y
        if game_world.camera:
            cam_x, cam_y = game_world.camera.apply(self.skrr.x, self.skrr.y)

        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, cam_x, cam_y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', cam_x, cam_y, img.w * self.skrr.scale, img.h * self.skrr.scale)


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

        self.skrr.set_attack_hitbox(
            width = 80, height = self.skrr.default_h * self.skrr.scale,
            center_offset_x = self.skrr.default_w // 2,
            damage = self.skrr.attack_power
        )

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

        if self.skrr.attack_type == 'A':
            if 4 <= self.skrr.frame < 10:
                self.skrr.get_attack_hitbox()
        elif self.skrr.attack_type == 'B':
            if 3 <= self.skrr.frame < 8:
                self.skrr.get_attack_hitbox()

    def exit(self, e):
        self.skrr.clear_attack_hitbox()
        pass

    def draw(self):
        if self.skrr.attack_type == 'A':
            img = self.skrr.images['AttackA'][int(self.frame_time * self.ACTION_PER_TIME) % len(self.skrr.images['AttackA'])]
        elif self.skrr.attack_type == 'B':
            img = self.skrr.images['AttackB'][int(self.frame_time * self.ACTION_PER_TIME) % len(self.skrr.images['AttackB'])]
        else:
            return

        cam_x, cam_y = self.skrr.x, self.skrr.y
        if game_world.camera:
            cam_x, cam_y = game_world.camera.apply(self.skrr.x, self.skrr.y)

        if self.attack_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, cam_x, cam_y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.attack_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', cam_x, cam_y, img.w * self.skrr.scale, img.h * self.skrr.scale)


class Dash:
    EFFECT_TIME_PER_ACTION = 0.05
    EFFECT_ACTION_PER_TIME = 1.0 / EFFECT_TIME_PER_ACTION
    EFFECT_FRAMES_PER_ACTION = 3

    def __init__(self, skrr):
        self.skrr = skrr
        self.minX = 0
        self.dash_distance = 0
        self.max_dash_distance = 200
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
        self.minX = self.skrr.images['Walk'][0].w * self.skrr.scale // 2 - 20
        self.dash_dir = self.skrr.face_dir
        self.is_air_dash = not self.skrr.is_grounded

        self.effect_x, self.effect_y = self.skrr.x, self.skrr.y - 10
        self.effect_frame_time = 0

        SoundManager.play_player_sound('Dash')

    def do(self):
        self.effect_frame_time += game_framework.frame_time

        if self.dash_distance >= 30:
            self.can_second_dash = True

        dash_move = DASH_SPEED_PPS * game_framework.frame_time

        # 타일맵 경계 체크
        if self.skrr.tile_map:
            max_x = self.skrr.tile_map.map_width * self.skrr.tile_map.tile_width
            can_move = (self.dash_distance < self.max_dash_distance and
                       ((self.dash_dir == 1 and self.skrr.x < max_x - self.minX) or
                        (self.dash_dir == -1 and self.skrr.x > self.minX)))
        else:
            can_move = (self.dash_distance < self.max_dash_distance and
                       ((self.dash_dir == 1 and self.skrr.x < get_canvas_width() - self.minX) or
                        (self.dash_dir == -1 and self.skrr.x > self.minX)))

        if can_move:
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
            effect_cam_x, effect_cam_y = self.effect_x, self.effect_y
            if game_world.camera:
                effect_cam_x, effect_cam_y = game_world.camera.apply(self.effect_x, self.effect_y)

            if self.dash_dir == 1:
                effect_img.clip_draw(0, 0, effect_img.w, effect_img.h, effect_cam_x, effect_cam_y, effect_img.w, effect_img.h)
            elif self.dash_dir == -1:
                effect_img.clip_composite_draw(0, 0, effect_img.w, effect_img.h, 0, 'h', effect_cam_x, effect_cam_y, effect_img.w, effect_img.h)

        img = self.skrr.images['Dash'][0]
        cam_x, cam_y = self.skrr.x, self.skrr.y
        if game_world.camera:
            cam_x, cam_y = game_world.camera.apply(self.skrr.x, self.skrr.y)

        if self.dash_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, cam_x, cam_y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.dash_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', cam_x, cam_y, img.w * self.skrr.scale, img.h * self.skrr.scale)


class Fall:
    TIME_PER_ACTION = 0.25
    ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
    FRAMES_PER_ACTION = 15

    def __init__(self, skrr):
        self.skrr = skrr
        self.minX = 0
        self.frame_time = 0
        self.has_played_intro = False  # 0, 1 프레임 재생 완료 여부

    def enter(self, e):
        self.skrr.frame = 0
        self.frame_time = 0
        self.has_played_intro = False
        self.skrr.jumping = True
        self.minX = self.skrr.images['Walk'][0].w * self.skrr.scale // 2 - 20

    def do(self):
        self.frame_time += game_framework.frame_time

        if not self.has_played_intro:
            frame_index = int(self.frame_time * self.ACTION_PER_TIME * 2)
            if frame_index >= 2:
                self.has_played_intro = True
                self.frame_time = 0
                self.skrr.frame = 2
            else:
                self.skrr.frame = frame_index
        else:
            loop_frame = int(self.frame_time * self.ACTION_PER_TIME * 3) % 3
            self.skrr.frame = 2 + loop_frame

        if self.skrr.is_grounded:
            if self.skrr.is_moving:
                self.skrr.state_machine.handle_event(('LAND_ON_GROUND', 'WALK'))
            else:
                self.skrr.state_machine.handle_event(('LAND_ON_GROUND', 'IDLE'))
            self.skrr.jumping = False
            return

        if self.skrr.is_moving:
            move_speed = RUN_SPEED_PPS * game_framework.frame_time
            new_x = self.skrr.x + self.skrr.face_dir * move_speed

            # 타일맵 경계 체크
            if self.skrr.tile_map:
                max_x = self.skrr.tile_map.map_width * self.skrr.tile_map.tile_width
                min_x = max(0, self.minX)
                if min_x <= new_x <= max_x - self.minX:
                    self.skrr.x = new_x
                else:
                    self.skrr.x = max(min_x, min(new_x, max_x - self.minX))
            else:
                min_x = max(0, self.minX)
                if min_x <= new_x <= get_canvas_width() - self.minX:
                    self.skrr.x = new_x
                else:
                    self.skrr.x = max(min_x, min(new_x, get_canvas_width() - self.minX))

    def exit(self, e):
        pass

    def draw(self):
        if not self.skrr.images['Fall']:
            return

        if self.skrr.frame < len(self.skrr.images['Fall']):
            img = self.skrr.images['Fall'][self.skrr.frame]
        else:
            img = self.skrr.images['Fall'][0]

        cam_x, cam_y = self.skrr.x, self.skrr.y
        if game_world.camera:
            cam_x, cam_y = game_world.camera.apply(self.skrr.x, self.skrr.y)

        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, cam_x, cam_y, img.w * self.skrr.scale,
                          img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', cam_x, cam_y, img.w * self.skrr.scale,
                                    img.h * self.skrr.scale)


class Dead:
    TIME_PER_ACTION = 0.7
    ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
    FRAMES_PER_ACTION = 6

    def __init__(self, skrr):
        self.skrr = skrr
        self.frame_time = 0
        self.death_timer = 0
        self.respawn_delay = 2.0  # 2초 후 리스폰

    def enter(self, e):
        self.skrr.frame = 0
        self.frame_time = 0
        self.death_timer = 0
        # 사망 시 물리 상태 초기화
        self.skrr.velocity_y = 0
        self.skrr.clear_attack_hitbox()
        self.skrr.dash_type = None
        self.skrr.jump_count = 0

    def do(self):
        self.frame_time += game_framework.frame_time
        self.death_timer += game_framework.frame_time
        self.skrr.frame = int(self.frame_time * self.ACTION_PER_TIME * self.FRAMES_PER_ACTION)

        # 2초 후 자동으로 리스폰
        if self.death_timer >= self.respawn_delay:
            self.skrr.state_machine.handle_event(('RESPAWN', None))

    def exit(self, e):
        pass

    def draw(self):
        img = self.skrr.images['Dead'][int(self.frame_time * self.ACTION_PER_TIME) % len(self.skrr.images['Dead'])]
        cam_x, cam_y = self.skrr.x, self.skrr.y
        if game_world.camera:
            cam_x, cam_y = game_world.camera.apply(self.skrr.x, self.skrr.y)

        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, cam_x, cam_y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', cam_x, cam_y, img.w * self.skrr.scale, img.h * self.skrr.scale)


class Reborn:
    TIME_PER_ACTION = 0.1
    ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
    FRAMES_PER_ACTION = 6

    def __init__(self, skrr):
        self.skrr = skrr
        self.frame_time = 0
        self.total_frames = 27 * 2

    def enter(self, e):
        self.skrr.frame = 0
        self.frame_time = 0

        # 스테이지 0으로 돌아가기
        import play_mode
        play_mode.load_stage(0)

        # HP 회복
        self.skrr.current_hp = self.skrr.max_hp

        # Stage0 시작 위치로 이동
        import SKRR
        start_x, start_y = SKRR.stage_start_positions[0]
        self.skrr.x = start_x
        self.skrr.y = start_y

        # 물리 상태 초기화
        self.skrr.velocity_y = 0
        self.skrr.is_grounded = False
        self.skrr.was_grounded = False
        self.skrr.jumping = False
        self.skrr.jump_count = 0

        # 방향 초기화
        self.skrr.face_dir = 1

        # 이동 상태 초기화
        self.skrr.is_moving = False
        self.skrr.key_pressed = {'left': False, 'right': False}

        # 대쉬 상태 초기화
        self.skrr.dash_type = None
        self.skrr.dash_last_use_time = 0

        # 공격 상태 초기화
        self.skrr.attack_type = None
        self.skrr.jumpattack_last_use_time = 0
        self.skrr.clear_attack_hitbox()

        self.skrr.active_hitbox = None
        self.skrr.attack_bounding_box = None
        self.skrr.hit_targets = set()
        self.skrr.hit_timestamps = {}  # 각 적을 마지막으로 타격한 시간 기록

        # 스킬 쿨타임 초기화
        self.skrr.skill_last_use_time = {
            'skill1': -5.0,
            'skill2': -8.0,
            'skill3': -12.0
        }

    def do(self):
        self.frame_time += game_framework.frame_time
        self.skrr.frame = int(self.frame_time * self.ACTION_PER_TIME * self.FRAMES_PER_ACTION)

        if self.skrr.frame >= self.total_frames:
            self.skrr.state_machine.handle_event(('ANIMATION_END', None))

    def exit(self, e):
        pass

    def draw(self):
        img = self.skrr.images['Reborn'][int(self.frame_time * self.ACTION_PER_TIME) % len(self.skrr.images['Reborn'])]
        cam_x, cam_y = self.skrr.x, self.skrr.y
        if game_world.camera:
            cam_x, cam_y = game_world.camera.apply(self.skrr.x, self.skrr.y)

        img.clip_draw(0, 0, img.w, img.h, cam_x, cam_y, img.w * self.skrr.scale, img.h * self.skrr.scale)



class Skill1:
    TIME_PER_ACTION = 0.6
    ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
    FRAMES_PER_ACTION = 7
    def __init__(self, skrr):
        self.skrr = skrr
        self.frame_time = 0
        self.total_frames = 7 * 3
        self.prev_frame = -1

    def enter(self, e):
        self.skrr.frame = 0
        self.frame_time = 0
        self.prev_frame = -1
        self.skrr.use_skill('skill1')  # 쿨타임 기록

        self.skrr.set_attack_hitbox(
            width=110, height=self.skrr.default_h * self.skrr.scale,
            damage=int(self.skrr.attack_power * 0.8),
            multi_hit=True,
            hit_interval=0.2
        )

    def do(self):
        minX = self.skrr.images['Walk'][0].w * self.skrr.scale // 2 - 20
        self.frame_time += game_framework.frame_time
        self.skrr.frame = int(self.frame_time * self.ACTION_PER_TIME * self.FRAMES_PER_ACTION)

        if self.skrr.frame % 3 == 0 and self.skrr.frame != self.prev_frame:
            SoundManager.play_player_sound('Skill1_hit')
        self.prev_frame = self.skrr.frame

        if self.skrr.tile_map:
            max_x = self.skrr.tile_map.map_width * self.skrr.tile_map.tile_width
            if self.skrr.x <= minX and self.skrr.face_dir == -1:
                self.skrr.x = minX
            elif self.skrr.x >= max_x - minX and self.skrr.face_dir == 1:
                self.skrr.x = max_x - minX
            else:
                self.skrr.x += self.skrr.face_dir * RUN_SPEED_PPS * game_framework.frame_time / 2
        else:
            if self.skrr.x <= minX and self.skrr.face_dir == -1:
                self.skrr.x = minX
            elif self.skrr.x >= get_canvas_width() - minX and self.skrr.face_dir == 1:
                self.skrr.x = get_canvas_width() - minX
            else:
                self.skrr.x += self.skrr.face_dir * RUN_SPEED_PPS * game_framework.frame_time / 2

        if self.skrr.frame >= self.total_frames:
            if self.skrr.frame >= self.total_frames:
                if self.skrr.is_grounded:
                    if self.skrr.key_pressed['left']:
                        self.skrr.face_dir = -1
                        self.skrr.state_machine.handle_event(('ANIMATION_END', 'WALK'))
                    elif self.skrr.key_pressed['right']:
                        self.skrr.face_dir = 1
                        self.skrr.state_machine.handle_event(('ANIMATION_END', 'WALK'))
                    else:
                        self.skrr.state_machine.handle_event(('ANIMATION_END', 'IDLE'))
            else:
                self.skrr.state_machine.handle_event(('ANIMATION_END', 'FALL'))

        self.skrr.get_attack_hitbox()

    def exit(self, e):
        self.skrr.clear_attack_hitbox()
        pass

    def draw(self):
        img = self.skrr.images['Skill1'][self.skrr.frame % len(self.skrr.images['Skill1'])]
        cam_x, cam_y = self.skrr.x, self.skrr.y
        if game_world.camera:
            cam_x, cam_y = game_world.camera.apply(self.skrr.x, self.skrr.y)

        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, cam_x, cam_y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', cam_x, cam_y, img.w * self.skrr.scale, img.h * self.skrr.scale)


class Skill2:
    TIME_PER_ACTION = 0.1
    ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
    FRAMES_PER_ACTION = 3

    def __init__(self, skrr):
        self.skrr = skrr
        self.frame_time = 0
        self.total_frames = 3 * 12
        self.effect_frame = 0
        self.effect_total_frame = len(self.skrr.images['Skill2_Effect']) * 3
        self.start_frame = 0
        self.start_total_frame = len(self.skrr.images['Skill2_Start'])
        self.prev_frame = -1

    def enter(self, e):
        self.skrr.frame = 0
        self.frame_time = 0
        self.skrr.use_skill('skill2')  # 쿨타임 기록
        self.prev_frame = -1

        self.skrr.set_attack_hitbox(
            width=500, height=100,
            center_offset_y=self.skrr.default_h,
            damage=int(self.skrr.attack_power),
            multi_hit=True,
            hit_interval=0.08
        )

    def do(self):
        self.frame_time += game_framework.frame_time
        self.skrr.frame = int(self.frame_time * self.ACTION_PER_TIME * self.FRAMES_PER_ACTION)
        self.effect_frame = int(self.frame_time * self.ACTION_PER_TIME * self.FRAMES_PER_ACTION)
        self.start_frame = int(self.frame_time * self.ACTION_PER_TIME * self.FRAMES_PER_ACTION)

        if self.skrr.frame % 2 == 0 and self.skrr.frame != self.prev_frame:
            SoundManager.play_player_sound('Skill2_hit')
        self.prev_frame = self.skrr.frame

        if self.skrr.frame >= self.total_frames:
            print('skill2 end')
            if self.skrr.key_pressed['left']:
                self.skrr.face_dir = -1
                self.skrr.state_machine.handle_event(('ANIMATION_END', 'WALK'))
            elif self.skrr.key_pressed['right']:
                self.skrr.face_dir = 1
                self.skrr.state_machine.handle_event(('ANIMATION_END', 'WALK'))
            else:
                self.skrr.state_machine.handle_event(('ANIMATION_END', 'IDLE'))

        self.skrr.get_attack_hitbox()

    def exit(self, e):
        self.skrr.clear_attack_hitbox()
        pass

    def draw(self):
        img = self.skrr.images['Skill2'][int(self.frame_time * self.ACTION_PER_TIME) % len(self.skrr.images['Skill2'])]
        skill2_start = self.skrr.images['Skill2_Start'][self.start_frame % len(self.skrr.images['Skill2_Start'])]
        skill2_effet = self.skrr.images['Skill2_Effect'][self.effect_frame % len(self.skrr.images['Skill2_Effect'])]
        cam_x, cam_y = self.skrr.x, self.skrr.y
        if game_world.camera:
            cam_x, cam_y = game_world.camera.apply(self.skrr.x, self.skrr.y)

        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, cam_x - 20 , cam_y + 25, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', cam_x + 20, cam_y + 25, img.w * self.skrr.scale, img.h * self.skrr.scale)

        if self.effect_frame < self.effect_total_frame:
            skill2_effet.clip_draw(0, 0, skill2_effet.w, skill2_effet.h, cam_x, cam_y + 40, skill2_effet.w * 1.5, skill2_effet.h * 1.5)
        if self.start_frame < self.start_total_frame:
            skill2_start.clip_draw(0, 0, skill2_start.w, skill2_start.h, cam_x, cam_y + 40, skill2_start.w * 2.5, skill2_start.h * 2)

class Skill3:
    TIME_PER_ACTION = 0.08
    ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
    FRAMES_PER_ACTION = 6
    SKILL3_SPEED_PPS = 3000  # 매우 빠른 이동 속도

    def __init__(self, skrr):
        self.skrr = skrr
        self.frame_time = 0
        self.total_frames = 6 * 6
        self.is_air_skill = False
        self.minX = 0
        self.target_distance = 150
        self.traveled_distance = 0
        self.movement_stopped = False

    def enter(self, e):
        self.skrr.frame = 0
        self.frame_time = 0
        self.skrr.use_skill('skill3')
        self.is_air_skill = not self.skrr.is_grounded and self.skrr.jump_count > 0
        self.traveled_distance = 0
        self.start_x = self.skrr.x
        self.target_distance = 150
        self.movement_stopped = False
        self.hitbox_initialized = False

        self.minX = self.skrr.images['Walk'][0].w * self.skrr.scale // 2 - 20
        if self.is_air_skill:
            SoundManager.play_player_sound('Skill3_air')
            self.total_frames = 6 * 18
            self.skrr.set_attack_hitbox(
                width=self.target_distance * 1.5,
                height=self.skrr.default_h * self.skrr.scale + 20,
                damage=int(self.skrr.attack_power),
                multi_hit=True,
                hit_interval=0.1
            )
            self.hitbox_initialized = True
        else:
            SoundManager.play_player_sound('Skill3_ground')
            self.total_frames = 6 * 6
            self.target_distance = 300

    def do(self):
        self.frame_time += game_framework.frame_time
        self.skrr.frame = int(self.frame_time * self.ACTION_PER_TIME * self.FRAMES_PER_ACTION)

        if not self.movement_stopped and self.traveled_distance < self.target_distance:
            move_speed = self.SKILL3_SPEED_PPS * game_framework.frame_time
            actual_move = min(move_speed, self.target_distance - self.traveled_distance)

            new_x = self.skrr.x + self.skrr.face_dir * actual_move

            if self.skrr.tile_map:
                max_x = self.skrr.tile_map.map_width * self.skrr.tile_map.tile_width
                min_x = max(0, self.minX)

                if new_x < min_x:
                    self.skrr.x = min_x
                    self.movement_stopped = True
                elif new_x > max_x - self.minX:
                    self.skrr.x = max_x - self.minX
                    self.movement_stopped = True
                else:
                    self.skrr.x = new_x
                    self.traveled_distance += actual_move
            else:
                min_x = max(0, self.minX)

                if new_x < min_x:
                    self.skrr.x = min_x
                    self.movement_stopped = True
                elif new_x > get_canvas_width() - self.minX:
                    self.skrr.x = get_canvas_width() - self.minX
                    self.movement_stopped = True
                else:
                    self.skrr.x = new_x
                    self.traveled_distance += actual_move

        if not self.is_air_skill:
            current_distance = abs(self.skrr.x - self.start_x)
            center_offset = -(current_distance / 2)

            if not self.hitbox_initialized:
                self.skrr.set_attack_hitbox(
                    width=current_distance,
                    height=self.skrr.default_h * self.skrr.scale + 20,
                    center_offset_x=center_offset,
                    center_offset_y=0,
                    damage=int(self.skrr.attack_power * 0.7),
                    multi_hit=True,
                    hit_interval=0.1
                )
                self.hitbox_initialized = True
            else:
                self.skrr.update_skill3_bb(center_offset, 0, width=current_distance)

            self.skrr.get_attack_hitbox()

        if self.skrr.frame >= self.total_frames:
            if self.skrr.is_grounded:
                if self.skrr.key_pressed['left']:
                    self.skrr.face_dir = -1
                    self.skrr.state_machine.handle_event(('ANIMATION_END', 'WALK'))
                elif self.skrr.key_pressed['right']:
                    self.skrr.face_dir = 1
                    self.skrr.state_machine.handle_event(('ANIMATION_END', 'WALK'))
                else:
                    self.skrr.state_machine.handle_event(('ANIMATION_END', 'IDLE'))
            else:
                if self.skrr.key_pressed['left']:
                    self.skrr.face_dir = -1
                elif self.skrr.key_pressed['right']:
                    self.skrr.face_dir = 1
                self.skrr.state_machine.handle_event(('ANIMATION_END', 'FALL'))

    def exit(self, e):
        if self.is_air_skill:
            self.skrr.x = self.start_x
            self.skrr.velocity_y = 0
        self.is_air_skill = False
        self.traveled_distance = 0
        self.movement_stopped = False
        self.skrr.clear_attack_hitbox()

    def draw(self):
        img = None
        if self.is_air_skill and 'Skill3_air' in self.skrr.images and len(self.skrr.images['Skill3_air']) > 0:
            img = self.skrr.images['Skill3_air'][int(self.frame_time * self.ACTION_PER_TIME) % len(self.skrr.images['Skill3_air'])]
        elif not self.is_air_skill and 'Skill3_ground' in self.skrr.images and len(self.skrr.images['Skill3_ground']) > 0:
            img = self.skrr.images['Skill3_ground'][int(self.frame_time * self.ACTION_PER_TIME) % len(self.skrr.images['Skill3_ground'])]

        if img is None:
            return

        cam_x, cam_y = self.skrr.x, self.skrr.y
        if game_world.camera:
            cam_x, cam_y = game_world.camera.apply(self.skrr.x, self.skrr.y)

        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, cam_x, cam_y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', cam_x, cam_y, img.w * self.skrr.scale, img.h * self.skrr.scale)
