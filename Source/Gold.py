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

    def update(self):
        self.frame = (self.frame + Gold.FRAMES_PER_ACTION * Gold.ACTION_PER_TIME * game_framework.frame_time) % Gold.FRAMES_PER_ACTION

        # 2초 체크
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
            print(f"Gold collected: +{self.gold_amount}, Total: {player.gold_amount}")

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

    def get_bb(self):
        size = 16 * self.scale
        return (self.x - size / 2, self.y - size / 2,
                self.x + size / 2, self.y + size / 2)

    def handle_collision(self, group, other):
        pass
