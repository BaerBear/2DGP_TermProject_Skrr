from pico2d import *
from ResourceManager import ResourceManager
import game_framework
import game_world
import SKRR
from Sound_Loader import SoundManager

FIRE_TIME_PER_ACTION = 0.05
FIRE_ACTION_PER_TIME = 1.0 / FIRE_TIME_PER_ACTION
FIRE_DURATION = 3.0

FIRE_DAMAGE = 10               # 불장판 데미지
FIRE_DAMAGE_INTERVAL = 0.5     # 피격 간격

class FireField:
    def __init__(self, x, y, boss_images):
        self.x = x
        self.y = y - 80
        self.scale_w = 2.5
        self.scale_h = 1.25
        self.frame = 0
        self.frame_time = 0
        self.alive_time = 0
        self.is_alive = True

        self.fire_images = boss_images.get('skill2_fire', [])

        # 멀티히트 데미지 시스템
        self.hit_targets = {}  # 타겟별 마지막 히트 시간 기록
        self.damage = FIRE_DAMAGE
        self.damage_interval = FIRE_DAMAGE_INTERVAL

        # 히트박스 크기 (조절 가능)
        if self.fire_images and len(self.fire_images) > 0:
            sample_img = self.fire_images[0]
            self.width = sample_img.w * self.scale_w
            self.height = sample_img.h * self.scale_h
        else:
            self.width = 100 * self.scale_w
            self.height = 50 * self.scale_h

    def get_bb(self):
        """데미지 판정 박스 (히트박스)"""
        return (self.x - self.width / 2.5, self.y - self.height / 2.5,
                self.x + self.width / 2.5, self.y + self.height / 2.5)

    def update(self):
        if not self.is_alive:
            return

        # 시간 업데이트
        self.frame_time += game_framework.frame_time
        self.alive_time += game_framework.frame_time

        # 지속 시간 체크
        if self.alive_time >= FIRE_DURATION:
            self.is_alive = False
            return

        # 프레임 업데이트
        if self.fire_images and len(self.fire_images) > 0:
            frame_count = len(self.fire_images)
            self.frame = int(self.frame_time * FIRE_ACTION_PER_TIME) % frame_count

        # 플레이어와 멀티히트 충돌 체크
        current_time = get_time()
        player = SKRR.get_player()
        if player and hasattr(player, 'get_bb'):
            if self.check_collision(player):
                # 플레이어를 아직 때리지 않았거나, 히트 간격이 지났으면 데미지 적용
                if (player not in self.hit_targets or
                    (current_time - self.hit_targets[player]) >= self.damage_interval):
                    self.apply_damage_to_player(player)
                    self.hit_targets[player] = current_time

    def check_collision(self, entity):
        """엔티티와의 충돌 체크"""
        left1, bottom1, right1, top1 = self.get_bb()
        left2, bottom2, right2, top2 = entity.get_bb()

        if left1 > right2: return False
        if right1 < left2: return False
        if top1 < bottom2: return False
        if bottom1 > top2: return False

        return True

    def apply_damage_to_player(self, player):
        """플레이어에게 데미지 적용"""
        if hasattr(player, 'get_damage'):
            player.get_damage(self.damage)
            SoundManager.play_enemy_sound('boss_hit_skill2')
            #print(f"FireField: Player takes {self.damage} damage! (Multi-hit)")

    def draw(self):
        if not self.is_alive:
            return

        if not self.fire_images or len(self.fire_images) == 0:
            return

        frame_index = min(self.frame, len(self.fire_images) - 1)
        img = self.fire_images[frame_index]

        cam_x, cam_y = self.x, self.y
        if game_world.camera:
            cam_x, cam_y = game_world.camera.apply(self.x, self.y)

        # 화염 그리기
        img.draw(cam_x, cam_y, self.width, self.height)

        # 디버그용 충돌 박스
        if game_framework.show_collision_boxes:
            from pico2d import draw_rectangle
            if game_world.camera:
                camera_x, camera_y = game_world.camera.get_position()
                left, bottom, right, top = self.get_bb()
                draw_rectangle(left - camera_x, bottom - camera_y,
                               right - camera_x, top - camera_y)
