from pico2d import *
from ResourceManager import ResourceManager
import game_framework
import game_world
import random

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION


class HitEffect:
    images = {}

    def __init__(self, effect_type, x, y, scale=1.0, flip_h=False):
        self.effect_type = effect_type
        if effect_type not in HitEffect.images:
            HitEffect.images[effect_type] = ResourceManager.get_effect_images(effect_type)
        self.images = HitEffect.images[effect_type]
        self.FRAMES_PER_ACTION = len(self.images)
        self.x = x - self.images[0].w / 2 * flip_h
        self.y = y
        self.scale = scale
        self.flip_h = flip_h  # 수평 뒤집기 여부
        self.frame = 0
        self.done = False
        self.alpha = 1.0

    def update(self):
        if not self.done:
            self.frame += game_framework.frame_time * self.FRAMES_PER_ACTION * ACTION_PER_TIME
            if self.frame >= self.FRAMES_PER_ACTION:
                self.done = True
            else:
                self.alpha = 1.0 - (self.frame / self.FRAMES_PER_ACTION)

    def draw(self):
        if not self.done:
            frame_index = int(self.frame)
            if frame_index < len(self.images):
                image = self.images[frame_index]

                from Camera import Camera
                camera = Camera.get_instance()
                if camera:
                    cam_x, cam_y = camera.apply(self.x, self.y)
                    image.opacify(self.alpha)

                    if self.flip_h:
                        # 수평 뒤집기
                        image.composite_draw(0, 'h', cam_x, cam_y, int(image.w * self.scale), int(image.h * self.scale))
                    else:
                        # 정상
                        image.composite_draw(0, '', cam_x, cam_y, int(image.w * self.scale), int(image.h * self.scale))

    def is_done(self):
        return self.done


def create_player_hit_effect(x, y):
    effect = HitEffect('hit_normal', x, y, scale=2.0)
    game_world.add_object(effect, 3)
    return effect


def create_enemy_hit_effect(x, y, enemy_direction):
    flip = (enemy_direction == 1)
    effect = HitEffect('skul_hit', x, y, scale=1.5, flip_h=flip)
    game_world.add_object(effect, 3)
    return effect


def create_skill3_hit_effect(x, y):
    effect = HitEffect('hit_skill3', x, y, scale=2, flip_h=random.choice([True, False]))
    game_world.add_object(effect, 3)
    return effect


def create_boss_hit_effect(x, y):
    effect = HitEffect('hit_grimReaper', x, y, scale=2, flip_h=random.choice([True, False]))
    game_world.add_object(effect, 3)
    return effect
