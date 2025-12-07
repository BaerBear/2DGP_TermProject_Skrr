from pico2d import *
from ResourceManager import ResourceManager
import game_framework
import game_world

TIME_PER_ACTION = 0.167
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8

class Gate:
    c_image = None
    o_image = None

    def __init__(self, x, y, next_stage, current_stage):
        self.x = x
        self.y = y
        self.activated = False
        self.scale = 1.5
        self.next_stage = next_stage
        self.current_stage = current_stage
        self.width = None
        self.height = None
        self.player_in_range = False
        self.frame = 0
        self.animation_time = 0.0

        if Gate.c_image is None:
            c_images = ResourceManager.get_object_images('gate_close')
            if isinstance(c_images, list) and len(c_images) > 0:
                Gate.c_image = c_images[0]
            else:
                Gate.c_image = c_images

            if Gate.c_image:
                self.width = Gate.c_image.w
                self.height = Gate.c_image.h
                print (f"Gate width set to {self.width}, height set to {self.height}")

        if Gate.o_image is None:
            Gate.o_image = ResourceManager.get_object_images('gate_open')

        if self.width is None and Gate.c_image:
            self.width = Gate.c_image.w
            self.height = Gate.c_image.h
            print (f"Gate width set to {self.width}, height set to {self.height}")

    def check_enemies_cleared(self):
        enemy_layer = 1
        if enemy_layer >= len(game_world.world):
            return True

        enemies = game_world.world[enemy_layer]

        from Boss import GrimReaper
        normal_enemies = [e for e in enemies if not isinstance(e, GrimReaper)]

        return len(normal_enemies) == 0

    def update(self):
        if self.activated:
            self.animation_time += game_framework.frame_time
            self.frame = int(self.animation_time * ACTION_PER_TIME) % FRAMES_PER_ACTION
        else:
            self.frame = 0
            self.frame_time = 0.0
            self.activated = self.check_enemies_cleared()

        # 플레이어와의 거리 체크
        self.check_player_range()

    def check_player_range(self):
        if not self.activated:
            self.player_in_range = False
            return

        # play_mode에서 플레이어 가져오기
        import play_mode
        player = play_mode.Skrr
        if not player:
            self.player_in_range = False
            return

        gate_bb = self.get_bb()
        player_bb = player.get_bb()

        gate_left, gate_bottom, gate_right, gate_top = gate_bb
        player_left, player_bottom, player_right, player_top = player_bb

        if (gate_left < player_right and
            gate_right > player_left and
            gate_bottom < player_top and
            gate_top > player_bottom):
            self.player_in_range = True
        else:
            self.player_in_range = False

    def get_bb(self):
        if self.width is None or self.height is None:
            return (0, 0, 0, 0)

        return (self.x - self.width / 2 + 50, self.y - self.height / 2,
                self.x + self.width / 2 - 50, self.y + self.height / 2 - 30)

    def draw(self):
        cam_x, cam_y = self.x, self.y
        if game_world.camera:
            cam_x, cam_y = game_world.camera.apply(self.x, self.y)

        if self.activated:
            if Gate.o_image and len(Gate.o_image) > 0:
                image = Gate.o_image[self.frame]
                image.clip_draw(0, 0, image.w, image.h, cam_x, cam_y, image.w * self.scale, image.h * self.scale)

                if game_framework.show_collision_boxes:
                    left, bottom, right, top = self.get_bb()
                    if game_world.camera:
                        camera_x, camera_y = game_world.camera.get_position()
                        draw_rectangle(left - camera_x, bottom - camera_y,
                                       right - camera_x, top - camera_y)
        else:
            if Gate.c_image:
                Gate.c_image.clip_draw(0, 0, Gate.c_image.w, Gate.c_image.h, cam_x, cam_y, Gate.c_image.w * self.scale, Gate.c_image.h * self.scale)

                if game_framework.show_collision_boxes:
                    left, bottom, right, top = self.get_bb()
                    if game_world.camera:
                        camera_x, camera_y = game_world.camera.get_position()
                        draw_rectangle(left - camera_x, bottom - camera_y,
                                       right - camera_x, top - camera_y)

    def handle_collision(self, group, other):
        if group == 'player:gate':
            pass

    def interact(self):
        if self.activated and self.player_in_range:
            # 다음 스테이지로 이동
            import play_mode
            play_mode.load_stage(self.next_stage)
            return True
        return False