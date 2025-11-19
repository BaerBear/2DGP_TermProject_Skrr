from pico2d import *
from Enemy import Enemy
from ResourceManager import ResourceManager
import SKRR
import game_framework
import game_world
import random

BOSS_WALK_SPEED_PPS = 80.0

class GrimReaper(Enemy):
    images = None

    def __init__(self, x, y):
        super().__init__(x, y)

        # 보스 기본 스탯
        self.hp = 2000
        self.max_hp = 2000
        self.velocity = BOSS_WALK_SPEED_PPS
        self.scale = 3

        # 공격 상태
        self.is_dashing = False
        self.dash_speed = BOSS_WALK_SPEED_PPS * 4.0
        self.dash_distance = 500
        self.dash_traveled = 0

        # 스킬 쿨다운
        self.skill1_cooldown = 8.0
        self.skill1_last_use = -8.0
        self.skill2_cooldown = 12.0
        self.skill2_last_use = -12.0
        self.dash_cooldown = 6.0
        self.dash_last_use = -6.0

        # 스킬 상태
        self.is_using_skill = False
        self.current_skill = None

        # 이미지 로드
        if not GrimReaper.images:
            GrimReaper.images = self.load_images()

        # 크기 조정
        if GrimReaper.images and 'idle' in GrimReaper.images and GrimReaper.images['idle']:
            sample_img = GrimReaper.images['idle'][0]
            self.width = sample_img.w * self.scale * 0.5
            self.height = sample_img.h * self.scale * 0.8
        else:
            self.width = 80 * self.scale
            self.height = 100 * self.scale

    @staticmethod
    def load_images():
        """보스 이미지 로드"""
        base_path = '..\\Resources\\Image\\Object\\GrimReaper\\'
        images = {}

        try:
            # Idle
            images['idle'] = []
            for i in range(6):
                img = load_image(base_path + f'Idle\\Idle_{i} #*.png')
                images['idle'].append(img)

            # Walk
            images['walk'] = []
            for i in range(6):
                img = load_image(base_path + f'Walk\\Walk_{i} #*.png')
                images['walk'].append(img)

            # AttackA (기본 공격)
            images['attack'] = []
            for i in range(9):
                img = load_image(base_path + f'AttackA\\AttackA_{i} #*.png')
                images['attack'].append(img)

            # Skill1 (스킬1)
            images['skill1'] = []
            for i in range(32):
                img = load_image(base_path + f'Skill1\\GrimReaper_Sentence_3_Hit_{i}.png')
                images['skill1'].append(img)

            # Skill2 (스킬2)
            images['skill2'] = []
            for i in range(80):
                img = load_image(base_path + f'Skill2\\GrimReaper_TheStake_Land_{i}.png')
                images['skill2'].append(img)

            print("Boss images loaded successfully")
        except Exception as e:
            print(f"Boss image loading error: {e}")

        return images

    def get_bb(self):
        """물리/타일 충돌용 박스"""
        if self.is_dashing:
            width_modifier = 0.8
        else:
            width_modifier = 1.0

        adjusted_width = self.width * width_modifier
        return (self.x - adjusted_width / 2, self.y - self.height / 2,
                self.x + adjusted_width / 2, self.y + self.height / 2)

    def get_hit_bb(self):
        """피격 박스"""
        if self.is_dashing:
            # 대쉬 중에는 히트박스 작게
            return (self.x - self.width / 3, self.y - self.height / 3,
                    self.x + self.width / 3, self.y + self.height / 3)
        else:
            # 일반 상태
            return (self.x - self.width / 2.5, self.y - self.height / 2.5,
                    self.x + self.width / 2.5, self.y + self.height / 2.5)

    def update(self):
        if not self.is_alive:
            return

        self.apply_gravity()
        self.check_tile_collision()

        player = SKRR.get_player()
        if not player:
            return

        self.dis_to_player = abs(self.x - player.x)
        current_time = get_time()

        # 스킬 사용 중이거나 대쉬 중이 아닐 때만 방향 전환
        if not self.is_using_skill and not self.is_dashing and not self.is_attacking:
            if player.x > self.x:
                self.face_dir = 1
            else:
                self.face_dir = -1

        # 대쉬 처리
        if self.is_dashing:
            self.state = 'DASH'
            move_distance = self.dash_speed * game_framework.frame_time
            self.x += move_distance * self.face_dir
            self.dash_traveled += move_distance

            if self.dash_traveled >= self.dash_distance:
                self.is_dashing = False
                self.dash_traveled = 0
                self.state = 'IDLE'

        # 스킬 사용 중 처리
        elif self.is_using_skill:
            if self.current_skill == 'SKILL1':
                # Skill1 지속 시간 체크
                skill_duration = len(GrimReaper.images.get('skill1', [])) * 0.1
                if self.frame_time >= skill_duration:
                    self.is_using_skill = False
                    self.current_skill = None
            elif self.current_skill == 'SKILL2':
                # Skill2 지속 시간 체크
                skill_duration = len(GrimReaper.images.get('skill2', [])) * 0.1
                if self.frame_time >= skill_duration:
                    self.is_using_skill = False
                    self.current_skill = None

        # 일반 행동 패턴
        else:
            detect_range = 700
            attack_range = 150
            skill_range = 400

            # 스킬 우선순위 체크
            if self.dis_to_player <= skill_range:
                # Skill2 사용 가능?
                if current_time - self.skill2_last_use >= self.skill2_cooldown:
                    self.use_skill2()
                    return
                # Skill1 사용 가능?
                elif current_time - self.skill1_last_use >= self.skill1_cooldown:
                    self.use_skill1()
                    return

            # 대쉬 공격 (중거리)
            if 200 <= self.dis_to_player <= 500:
                if current_time - self.dash_last_use >= self.dash_cooldown:
                    self.start_dash()
                    return

            # 기본 공격 (근거리)
            if self.dis_to_player <= attack_range:
                if current_time - self.attack_last_use_time >= self.attack_cooldown_time:
                    self.state = 'ATTACK'
                    self.is_attacking = True
                    self.attack_last_use_time = current_time
                elif not self.is_attacking:
                    self.state = 'IDLE'

            # 이동
            elif self.dis_to_player <= detect_range:
                self.state = 'WALK'
                self.x += self.velocity * self.face_dir * game_framework.frame_time

            else:
                self.state = 'IDLE'

        # 상태 변경 체크
        if self.state != self.prev_state:
            self.frame_time = 0
            self.prev_state = self.state

        self.frame_time += game_framework.frame_time

        # 프레임 업데이트
        self.update_frame()

        # 공격 종료 체크
        if self.state == 'ATTACK' and self.is_attacking:
            attack_duration = len(GrimReaper.images.get('attack', [])) * 0.1
            if self.frame_time >= attack_duration:
                self.is_attacking = False

    def update_frame(self):
        """프레임 업데이트"""
        if self.state == 'IDLE':
            frame_count = len(GrimReaper.images.get('idle', []))
            if frame_count > 0:
                self.frame = int(self.frame_time * 6.0) % frame_count

        elif self.state == 'WALK' or self.state == 'DASH':
            frame_count = len(GrimReaper.images.get('walk', []))
            if frame_count > 0:
                self.frame = int(self.frame_time * 8.0) % frame_count

        elif self.state == 'ATTACK':
            frame_count = len(GrimReaper.images.get('attack', []))
            if frame_count > 0:
                self.frame = int(self.frame_time * 10.0) % frame_count

        elif self.state == 'SKILL1':
            frame_count = len(GrimReaper.images.get('skill1', []))
            if frame_count > 0:
                self.frame = int(self.frame_time * 10.0) % frame_count

        elif self.state == 'SKILL2':
            frame_count = len(GrimReaper.images.get('skill2', []))
            if frame_count > 0:
                self.frame = int(self.frame_time * 10.0) % frame_count

    def start_dash(self):
        """대쉬 시작"""
        self.is_dashing = True
        self.dash_traveled = 0
        self.dash_last_use = get_time()
        self.state = 'DASH'

    def use_skill1(self):
        """스킬1 사용"""
        self.is_using_skill = True
        self.current_skill = 'SKILL1'
        self.state = 'SKILL1'
        self.skill1_last_use = get_time()

    def use_skill2(self):
        """스킬2 사용"""
        self.is_using_skill = True
        self.current_skill = 'SKILL2'
        self.state = 'SKILL2'
        self.skill2_last_use = get_time()

    def draw(self):
        """보스 그리기"""
        if not GrimReaper.images:
            return

        img = None

        # 상태에 따른 이미지 선택
        if self.state == 'IDLE':
            if 'idle' in GrimReaper.images and GrimReaper.images['idle']:
                img = GrimReaper.images['idle'][self.frame % len(GrimReaper.images['idle'])]

        elif self.state == 'WALK' or self.state == 'DASH':
            if 'walk' in GrimReaper.images and GrimReaper.images['walk']:
                img = GrimReaper.images['walk'][self.frame % len(GrimReaper.images['walk'])]

        elif self.state == 'ATTACK':
            if 'attack' in GrimReaper.images and GrimReaper.images['attack']:
                img = GrimReaper.images['attack'][self.frame % len(GrimReaper.images['attack'])]

        elif self.state == 'SKILL1':
            if 'skill1' in GrimReaper.images and GrimReaper.images['skill1']:
                img = GrimReaper.images['skill1'][self.frame % len(GrimReaper.images['skill1'])]

        elif self.state == 'SKILL2':
            if 'skill2' in GrimReaper.images and GrimReaper.images['skill2']:
                img = GrimReaper.images['skill2'][self.frame % len(GrimReaper.images['skill2'])]

        if img:
            cam_x, cam_y = self.x, self.y
            if game_world.camera:
                cam_x, cam_y = game_world.camera.apply(self.x, self.y)

            if self.face_dir == 1:
                img.clip_draw(0, 0, img.w, img.h, cam_x, cam_y, img.w * self.scale, img.h * self.scale)
            else:
                img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', cam_x, cam_y, img.w * self.scale, img.h * self.scale)

        # 체력바 그리기
        self.draw_hp_bar()

        # 충돌박스 그리기
        self.draw_collision_box()

    def draw_hp_bar(self):
        """보스 체력바 그리기"""
        if game_world.camera:
            cam_x, cam_y = game_world.camera.apply(self.x, self.y)

            hp_bar_width = 200
            hp_bar_height = 15
            hp_ratio = max(0, self.hp / self.max_hp)

            # 체력바 배경 (어두운 빨간색)
            bar_y = cam_y + self.height / 2 + 30

            # 외곽선
            draw_rectangle(cam_x - hp_bar_width/2 - 2, bar_y - 2,
                         cam_x + hp_bar_width/2 + 2, bar_y + hp_bar_height + 2)

            # 현재 체력바 (초록->노랑->빨강)
            if hp_ratio > 0:
                current_width = hp_bar_width * hp_ratio
                # TODO: 색상별로 체력바 그리기 (나중에 구현)

    def draw_collision_box(self):
        """충돌 박스 그리기 (디버그용)"""
        if SKRR.SKRR.show_collision_box:
            from pico2d import draw_rectangle
            if game_world.camera:
                camera_x, camera_y = game_world.camera.get_position()

                # 물리 충돌 박스
                left, bottom, right, top = self.get_bb()
                draw_rectangle(left - camera_x, bottom - camera_y,
                             right - camera_x, top - camera_y)

                # 피격 박스
                hit_left, hit_bottom, hit_right, hit_top = self.get_hit_bb()
                draw_rectangle(hit_left - camera_x, hit_bottom - camera_y,
                             hit_right - camera_x, hit_top - camera_y)

