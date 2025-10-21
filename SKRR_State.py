from pico2d import get_canvas_width

class Idle:
    def __init__(self, skrr):
        self.skrr = skrr

    def enter(self):
        self.skrr.frame = 0

    def do(self):
        self.skrr.frame += 1

    def exit(self):
        pass

    def draw(self):
        img = self.skrr.Idle_image[self.skrr.frame // 10 % 4]
        if self.skrr.face_dir == 1:
            img.clip_draw(0, 0, img.w, img.h, self.skrr.x, self.skrr.y,
                          img.w * self.skrr.scale, img.h * self.skrr.scale)
        elif self.skrr.face_dir == -1:
            img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', self.skrr.x, self.skrr.y,
                                    img.w * self.skrr.scale, img.h * self.skrr.scale)

class Wait:
    def __init__(self, skrr):
        self.skrr = skrr

    def enter(self):
        self.skrr.frame = 0

    def do(self):
        self.skrr.frame += 1

    def exit(self):
        pass

    def draw(self):
        pass

class Walk:
    def __init__(self, skrr):
        self.skrr = skrr

    def enter(self):
        self.skrr.frame = 0

    def do(self):
        self.skrr.frame += 1

    def exit(self):
        pass

    def draw(self):
        pass

class Jump:
    def __init__(self, skrr):
        self.skrr = skrr

    def enter(self):
        self.skrr.frame = 0

    def do(self):
        self.skrr.frame += 1

    def exit(self):
        pass

    def draw(self):
        pass

class JumpAttack:
    def __init__(self, skrr):
        self.skrr = skrr

    def enter(self):
        self.skrr.frame = 0

    def do(self):
        self.skrr.frame += 1

    def exit(self):
        pass

    def draw(self):
        pass


class Attack:
    def __init__(self, skrr):
        self.skrr = skrr

    def enter(self):
        self.skrr.frame = 0

    def do(self):
        self.skrr.frame += 1

    def exit(self):
        pass

    def draw(self):
        pass


class Dash:
    def __init__(self, skrr):
        self.skrr = skrr

    def enter(self):
        self.skrr.frame = 0

    def do(self):
        self.skrr.frame += 1

    def exit(self):
        pass

    def draw(self):
        pass

class Fall:
    def __init__(self, skrr):
        self.skrr = skrr

    def enter(self):
        self.skrr.frame = 0

    def do(self):
        self.skrr.frame += 1

    def exit(self):
        pass

    def draw(self):
        pass

class Dead:
    def __init__(self, skrr):
        self.skrr = skrr

    def enter(self):
        self.skrr.frame = 0

    def do(self):
        self.skrr.frame += 1

    def exit(self):
        pass

    def draw(self):
        pass

class Reborn:
    def __init__(self, skrr):
        self.skrr = skrr

    def enter(self):
        self.skrr.frame = 0

    def do(self):
        self.skrr.frame += 1

    def exit(self):
        pass

    def draw(self):
        pass


















