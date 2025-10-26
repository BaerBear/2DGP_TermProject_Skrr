from pico2d import delay, get_canvas_width, get_time
from Sound_Loader import SoundManager

class Idle:
    def __init__(self, skrr):
        self.skrr = skrr
        self.timer = 0

    def enter(self, e):
        self.skrr.frame = 0
        self.skrr.is_grounded = True
        self.skrr.jump_count = 0
        self.timer = get_time()

    def do(self):
        self.skrr.frame = self.skrr.frame + 1
        delay(0.001)
        if get_time() - self.timer > 4.0:
            self.skrr.state_machine.handle_event(('TIME_OUT', None))

    def exit(self, e):
        pass

    def draw(self):
        img = self.skrr.Idle_image[self.skrr.frame // 10 % len(self.skrr.Idle_image)]
        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)


class Wait:
    def __init__(self, skrr):
        self.skrr = skrr

    def enter(self, e):
        self.skrr.frame = 0

    def do(self):
        self.skrr.frame = self.skrr.frame + 1
        delay(0.06)
        if self.skrr.frame >= 46:
            self.skrr.state_machine.handle_event(('ANIMATION_END', None))

    def exit(self, e):
        pass

    def draw(self):
        img = self.skrr.Wait_image[self.skrr.frame % len(self.skrr.Wait_image)]
        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)


class Walk:
    def __init__(self, skrr):
        self.skrr = skrr

    def enter(self, e):
        self.skrr.frame = 0

    def do(self):
        minX = self.skrr.Walk_image[0].w * self.skrr.scale // 2 - 10
        self.skrr.frame = self.skrr.frame + 1
        delay(0.01)

        if not self.skrr.is_moving:
            self.skrr.state_machine.handle_event(('STOP_MOVING', None))
            return

        if self.skrr.x <= minX and self.skrr.face_dir == -1:
            self.skrr.x = minX
        elif self.skrr.x >= get_canvas_width() - minX and self.skrr.face_dir == 1:
            self.skrr.x = get_canvas_width() - minX
        else:
            self.skrr.x += self.skrr.face_dir * 5

    def exit(self, e):
        pass

    def draw(self):
        img = self.skrr.Walk_image[self.skrr.frame // 3 % len(self.skrr.Walk_image)]
        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)


class Jump:
    def __init__(self, skrr):
        self.skrr = skrr
        self.minX = 0
        self.gravity = -0.8
        self.jump_power = 15
        self.effect_x = None
        self.effect_y = None
        self.effect_frame = 0

    def enter(self, e):
        self.skrr.frame = 0
        self.minX = self.skrr.Walk_image[0].w * self.skrr.scale // 2 - 10
        self.skrr.jumping = True
        if self.skrr.jump_count == 0:
            self.skrr.jump_count = 1
            self.skrr.is_grounded = False
            self.skrr.velocity_y = self.jump_power
            SoundManager.play_player_sound('Jump')
        elif self.skrr.jump_count == 1:
            self.skrr.jump_count = 2
            self.skrr.velocity_y = self.jump_power
            self.effect_x = self.skrr.x
            self.effect_y = self.skrr.y
            self.effect_frame = 0
            SoundManager.play_player_sound('Jump_air')

    def do(self):
        self.skrr.frame = self.skrr.frame + 1
        delay(0.003)

        if self.effect_y is not None:
            self.effect_frame += 1

        # 중력 적용
        self.skrr.velocity_y += self.gravity
        self.skrr.y += self.skrr.velocity_y

        # 낙하 시작 감지
        if self.skrr.velocity_y < 0 and not self.skrr.is_grounded:
            self.skrr.state_machine.handle_event(('START_FALLING', None))
            return

        # 좌우 이동
        if self.skrr.is_moving:
            move_speed = 5
            new_x = self.skrr.x + self.skrr.face_dir * move_speed

            # 화면 경계 체크 (임시)
            if self.minX <= new_x <= get_canvas_width() - self.minX:
                self.skrr.x = new_x

    def exit(self, e):
        self.effect_x = None
        self.effect_y = None
        self.effect_frame = 0

    def draw(self):
        img = self.skrr.Jump_image[self.skrr.frame // 5 % len(self.skrr.Jump_image)]
        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)

        if self.effect_y is not None and self.effect_frame < 20:
            if hasattr(self.skrr, 'JumpEffect_image') and self.skrr.JumpEffect_image:
                effect_img = self.skrr.JumpEffect_image[self.effect_frame // 3 % len(self.skrr.JumpEffect_image)]
                effect_img.clip_draw(0, 0, effect_img.w, effect_img.h, self.effect_x, self.effect_y,
                                     effect_img.w * self.skrr.scale, effect_img.h * self.skrr.scale)


class JumpAttack:
    def __init__(self, skrr):
        self.skrr = skrr
        self.minX = 0
        self.gravity = -0.8

    def enter(self, e):
        self.skrr.frame = 0
        self.skrr.jumpattack_last_use_time = get_time()
        self.minX = self.skrr.Walk_image[0].w * self.skrr.scale // 2 - 10

    def do(self):
        self.skrr.frame = self.skrr.frame + 1
        delay(0.01)

        # 중력 적용
        self.skrr.velocity_y += self.gravity
        self.skrr.y += self.skrr.velocity_y

        # 좌우 이동
        if self.skrr.is_moving:
            move_speed = 5
            new_x = self.skrr.x + self.skrr.face_dir * move_speed

            # 화면 경계 체크 (임시)
            if self.minX <= new_x <= get_canvas_width() - self.minX:
                self.skrr.x = new_x

        if self.skrr.frame >= 10:
            self.skrr.state_machine.handle_event(('ANIMATION_END', None))

    def exit(self, e):
        pass

    def draw(self):
        img = self.skrr.JumpAttack_image[self.skrr.frame // 4 % len(self.skrr.JumpAttack_image)]
        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)


class Attack:
    def __init__(self, skrr):
        self.skrr = skrr

    def enter(self, e):
        self.skrr.frame = 0
        from Event_Checker import attack_down, combo_available
        if attack_down(e) and self.skrr.attack_type == 'A' and self.skrr.frame >= 6:
            self.skrr.attack_type = 'B'
        elif self.skrr.attack_type is None or not combo_available(e):
            self.skrr.attack_type = 'A'

    def do(self):
        self.skrr.frame = self.skrr.frame + 1
        delay(0.02)

        if self.skrr.attack_type == 'A' and self.skrr.frame >= 15:
            self.skrr.state_machine.handle_event(('ANIMATION_END', None))
        elif self.skrr.attack_type == 'B' and self.skrr.frame >= 12:
            self.skrr.state_machine.handle_event(('ANIMATION_END', None))

    def exit(self, e):
        if self.skrr.attack_type == 'A' and self.skrr.frame >= 15:
            self.skrr.attack_type = None
        elif self.skrr.attack_type == 'B' and self.skrr.frame >= 12:
            self.skrr.attack_type = None

    def draw(self):
        if self.skrr.attack_type == 'A':
            img = self.skrr.AttackA_image[self.skrr.frame // 3 % len(self.skrr.AttackA_image)]
        elif self.skrr.attack_type == 'B':
            img = self.skrr.AttackB_image[self.skrr.frame // 3 % len(self.skrr.AttackB_image)]
        else:
            return

        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)


class Dash:
    def __init__(self, skrr):
        self.skrr = skrr
        self.minX = 0
        self.dash_distance = 0
        self.max_dash_distance = 150
        self.can_second_dash = False
        self.dash_dir = None
        self.is_air_dash = False

        self.effect_frame = 0
        self.effect_x, self.effect_y = None, None

    def enter(self, e):
        self.skrr.frame = 0
        if self.skrr.dash_type == 0:
            self.dash_distance = 0
            self.can_second_dash = False
        self.minX = self.skrr.Walk_image[0].w * self.skrr.scale // 2 - 10
        self.dash_dir = self.skrr.face_dir
        self.is_air_dash = not self.skrr.is_grounded

        self.effect_x, self.effect_y = self.skrr.x, self.skrr.y - 10
        self.effect_frame = 0
        self.skrr.is_invincible = True

        SoundManager.play_player_sound('Dash')

    def do(self):
        delay(0.007)
        self.effect_frame += 1
        if self.dash_distance >= 30:
            self.can_second_dash = True

        if (self.dash_distance < self.max_dash_distance
                and ((self.dash_dir == 1 and self.skrr.x < get_canvas_width() - self.minX)
                     or (self.dash_dir == -1 and self.skrr.x > self.minX))):
            self.skrr.x += self.dash_dir * 10
            self.dash_distance += 10
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

        if self.skrr.key_pressed['left'] and not self.skrr.key_pressed['right']:
            self.skrr.face_dir = -1
        elif self.skrr.key_pressed['right'] and not self.skrr.key_pressed['left']:
            self.skrr.face_dir = 1

    def draw(self):
        if hasattr(self.skrr, 'DashEffect_image') and self.skrr.DashEffect_image:
            effect_img = self.skrr.DashEffect_image[self.effect_frame // 2 % len(self.skrr.DashEffect_image)]
            if self.dash_dir == 1:
                effect_img.clip_draw(0, 0, effect_img.w, effect_img.h, self.effect_x, self.effect_y, effect_img.w, effect_img.h)
            elif self.dash_dir == -1:
                effect_img.clip_composite_draw(0, 0, effect_img.w, effect_img.h, 0, 'h', self.effect_x, self.effect_y, effect_img.w, effect_img.h)
        img = self.skrr.Dash_image[0]
        if self.dash_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.dash_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)



class Fall:
    def __init__(self, skrr):
        self.skrr = skrr
        self.minX = 0
        self.gravity = -0.8

    def enter(self, e):
        self.skrr.frame = 0
        self.skrr.jumping = True
        self.minX = self.skrr.Walk_image[0].w * self.skrr.scale // 2 - 10

    def do(self):
        self.skrr.frame = self.skrr.frame + 1
        delay(0.003)

        # 중력 적용
        self.skrr.velocity_y += self.gravity
        self.skrr.y += self.skrr.velocity_y

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

        # 좌우 이동
        if self.skrr.is_moving:
            move_speed = 5
            new_x = self.skrr.x + self.skrr.face_dir * move_speed

            # 화면 경계 체크 (임시)
            if self.minX <= new_x <= get_canvas_width() - self.minX:
                self.skrr.x = new_x

    def exit(self, e):
        pass

    def draw(self):
        if not self.skrr.Fall_image:
            return

        idx = (self.skrr.frame // 5) % len(self.skrr.Fall_image)
        img = self.skrr.Fall_image[idx]
        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale,
                          img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale,
                                    img.h * self.skrr.scale)


class Dead:
    def __init__(self, skrr):
        self.skrr = skrr

    def enter(self, e):
        self.skrr.frame = 0

    def do(self):
        self.skrr.frame = self.skrr.frame + 1
        delay(0.05)
        if self.skrr.frame >= 30:
            self.skrr.state_machine.handle_event(('ANIMATION_END', None))

    def exit(self, e):
        pass

    def draw(self):
        img = self.skrr.Dead_image[self.skrr.frame // 3 % len(self.skrr.Dead_image)]
        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)


class Reborn:
    def __init__(self, skrr):
        self.skrr = skrr

    def enter(self, e):
        self.skrr.frame = 0

    def do(self):
        self.skrr.frame = self.skrr.frame + 1
        delay(0.02)
        if self.skrr.frame >= 78:
            self.skrr.state_machine.handle_event(('ANIMATION_END', None))

    def exit(self, e):
        pass

    def draw(self):
        img = self.skrr.Reborn_image[self.skrr.frame // 3 % len(self.skrr.Reborn_image)]
        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale, img.h * self.skrr.scale)