from pico2d import *
import game_framework
import game_world
from Sound_Loader import SoundManager
import SKRR
from ResourceManager import ResourceManager

class Gold:
    images = None

    TIME_PER_ACTION = 1.0
    ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
    FRAMES_PER_ACTION = 30
    LIFETIME = 2.0

    @classmethod
    def load_images(cls):
        if cls.images is None:
            cls.images = ResourceManager.get_object_images('coin')

    def __init__(self, x, y, gold_amount=10):
        Gold.load_images()

        self.x, self.y = x, y
        self.gold_amount = gold_amount
        self.frame = 0
        self.scale = 1

        self.creation_time = get_time()
        self.is_collected = False

        self.velocity_y = 0
        self.gravity = -1000  # 중력 가속도
        self.is_grounded = False
        self.tile_map = None

        self.width = 16 * self.scale
        self.height = 16 * self.scale

    def set_tile_map(self, tile_map):
        self.tile_map = tile_map

    def get_bb(self):
        return (self.x - self.width / 2, self.y - self.height / 2,
                self.x + self.width / 2, self.y + self.height / 2)

    def apply_gravity(self):
        if not self.is_grounded:
            self.velocity_y += self.gravity * game_framework.frame_time
            self.y += self.velocity_y * game_framework.frame_time

    def check_tile_collision(self):
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
        left, bottom, right, top = self.get_bb()

        overlap_left = right - tile['left']
        overlap_right = tile['right'] - left
        overlap_top = tile['top'] - bottom
        overlap_bottom = top - tile['bottom']

        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

        if min_overlap == overlap_top and self.velocity_y <= 0:
            self.y = tile['top'] + self.height / 2
            self.velocity_y = 0
            return True

        return False

    def handle_platform_collision(self, tile):
        left, bottom, right, top = self.get_bb()

        if self.velocity_y <= 0 and bottom <= tile['top'] and bottom >= tile['top'] - 10:
            self.y = tile['top'] + self.height / 2
            self.velocity_y = 0
            return True

        return False

    def update(self):
        self.apply_gravity()

        self.check_tile_collision()

        self.frame = (self.frame + Gold.FRAMES_PER_ACTION *
                     Gold.ACTION_PER_TIME * game_framework.frame_time) % Gold.FRAMES_PER_ACTION

        elapsed_time = get_time() - self.creation_time
        if elapsed_time >= Gold.LIFETIME and not self.is_collected:
            self.collect()

    def collect(self):
        if self.is_collected:
            return

        self.is_collected = True

        player = SKRR.get_player()
        if player:
            player.gold_amount += self.gold_amount

        SoundManager.play_object_sound('drop_gold')

        game_world.remove_object(self)

    def draw(self):
        frame_index = int(self.frame)
        if 0 <= frame_index < len(Gold.images):
            cam_x, cam_y = self.x, self.y
            if game_world.camera:
                cam_x, cam_y = game_world.camera.apply(self.x, self.y)

            Gold.images[frame_index].draw(cam_x, cam_y,
                                         Gold.images[frame_index].w * self.scale,
                                         Gold.images[frame_index].h * self.scale)

    def handle_collision(self, group, other):
        pass
