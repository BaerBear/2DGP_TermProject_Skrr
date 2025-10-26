from pico2d import delay, get_canvas_width, get_time

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
        if get_time() - self.timer > 4.0:
            self.skrr.state_machine.handle_event(('TIME_OUT', None))

    def exit(self, e):
        pass

    def draw(self):
        img = self.skrr.Idle_image[self.skrr.frame // 10 % 4]
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
        self.skrr.frame += 1
        if self.skrr.frame >= 46:
            self.skrr.state_machine.handle_event(('ANIMATION_END', None))

    def exit(self, e):
        pass

    def draw(self):
        img = self.skrr.Wait_image[self.skrr.frame % 47]
        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale,
                          img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale,
                                    img.h * self.skrr.scale)


class Walk:
    def __init__(self, skrr):
        self.skrr = skrr

    def enter(self, e):
        self.skrr.frame = 0

    def do(self):
        self.skrr.frame += 1

    def exit(self, e):
        pass

    def draw(self):
        img = self.skrr.Walk_image[self.skrr.frame // 3 % 8]
        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale,
                          img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale,
                                    img.h * self.skrr.scale)


class Jump:
    def __init__(self, skrr):
        self.skrr = skrr

    def enter(self, e):
        self.skrr.frame = 0

    def do(self):
        self.skrr.frame += 1

    def exit(self, e):
        pass

    def draw(self):
        img = self.skrr.Jump_image[self.skrr.frame // 5 % 2]
        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale,
                          img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale,
                                    img.h * self.skrr.scale)

        if self.effect_y is not None and self.effect_frame < 20:
            if hasattr(self.skrr, 'JumpEffect_image') and self.skrr.JumpEffect_image:
                effect_img = self.skrr.JumpEffect_image[self.effect_frame // 3 % len(self.skrr.JumpEffect_image)]
                effect_img.clip_draw(0, 0, effect_img.w, effect_img.h, self.effect_x, self.effect_y,
                                     effect_img.w * self.skrr.scale, effect_img.h * self.skrr.scale)


class JumpAttack:
    def __init__(self, skrr):
        self.skrr = skrr

    def enter(self, e):
        self.skrr.frame = 0

    def do(self):
        self.skrr.frame += 1

    def exit(self, e):
        pass

    def draw(self):
        img = self.skrr.JumpAttack_image[self.skrr.frame // 4 % 2]
        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale,
                          img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale,
                                    img.h * self.skrr.scale)


class Attack:
    def __init__(self, skrr):
        self.skrr = skrr

    def enter(self, e):
        self.skrr.frame = 0

    def do(self):
        self.skrr.frame += 1

    def exit(self, e):
        pass

    def draw(self):
        if self.skrr.attack_type == 'A':
            img = self.skrr.AttackA_image[self.skrr.frame // 3 % 5]
        elif self.skrr.attack_type == 'B':
            img = self.skrr.AttackB_image[self.skrr.frame // 3 % 4]
        else:
            return

        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale,
                          img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale,
                                    img.h * self.skrr.scale)


class Dash:
    def __init__(self, skrr):
        self.skrr = skrr

    def enter(self, e):
        self.skrr.frame = 0

    def do(self):
        self.skrr.frame += 1

    def exit(self, e):
        pass

    def draw(self):
        img = self.skrr.Dash_image[0]
        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale,
                          img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale,
                                    img.h * self.skrr.scale)


class Fall:
    def __init__(self, skrr):
        self.skrr = skrr

    def enter(self, e):
        self.skrr.frame = 0

    def do(self):
        self.skrr.frame += 1

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
        self.skrr.frame += 1
        if self.skrr.frame >= 60:
            self.skrr.state_machine.handle_event(('ANIMATION_END', None))

    def exit(self, e):
        pass

    def draw(self):
        img = self.skrr.Dead_image[self.skrr.frame // 6 % 10]
        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale,
                          img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale,
                                    img.h * self.skrr.scale)


class Reborn:
    def __init__(self, skrr):
        self.skrr = skrr

    def enter(self, e):
        self.skrr.frame = 0

    def do(self):
        self.skrr.frame += 1
        if self.skrr.frame >= 130:
            self.skrr.state_machine.handle_event(('ANIMATION_END', None))

    def exit(self, e):
        pass

    def draw(self):
        img = self.skrr.Reborn_image[self.skrr.frame // 5 % 26]
        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y, img.w * self.skrr.scale,
                          img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y, img.w * self.skrr.scale,
                                    img.h * self.skrr.scale)


















