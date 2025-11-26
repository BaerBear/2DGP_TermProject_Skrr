from pico2d import *
from Enemy import Enemy
from ResourceManager import ResourceManager
import SKRR
import game_framework
import game_world

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

        # Skill1 전용 변수 (고속 돌진)
        self.skill1_phase = 'READY'  # READY, DASHING, LANDING
        self.skill1_start_x = 0
        self.skill1_start_y = 0
        self.skill1_target_x = 0
        self.skill1_target_y = 0
        self.skill1_dash_speed = 1200.0  # 매우 빠른 속도
        self.skill1_landing_timer = 0
        self.skill1_landing_duration = 0.7  # 착지 모션 시간 (7프레임 * 0.1)

        # 이미지 로드
        if not GrimReaper.images:
            GrimReaper.images = ResourceManager.get_boss_images('GrimReaper')

        # 크기 조정
        if GrimReaper.images and 'idle' in GrimReaper.images and GrimReaper.images['idle']:
            sample_img = GrimReaper.images['idle'][0]
            self.width = sample_img.w * self.scale * 0.5
            self.height = sample_img.h * self.scale * 0.8
        else:
            self.width = 80 * self.scale
            self.height = 100 * self.scale

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
                # Skill1 전용 업데이트 호출
                self.update_skill1()
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
            # Skill1은 별도로 처리 (단계별로 다름)
            pass

        elif self.state == 'SKILL2':
            frame_count = len(GrimReaper.images.get('skill2', []))
            if frame_count > 0:
                self.frame = int(self.frame_time * 10.0) % frame_count

    def update_skill1(self):
        """Skill1 (고속 돌진) 업데이트"""
        if self.skill1_phase == 'READY':
            # 준비 단계: 0번 모션 유지
            self.frame = 0
            # 바로 돌진 시작
            self.skill1_phase = 'DASHING'

        elif self.skill1_phase == 'DASHING':
            # 돌진 중: 목표 지점까지 고속 이동
            dx = self.skill1_target_x - self.x
            dy = self.skill1_target_y - self.y
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance > 10:  # 아직 도착 안함
                move_distance = self.skill1_dash_speed * game_framework.frame_time
                if move_distance >= distance:
                    # 도착
                    self.x = self.skill1_target_x
                    self.y = self.skill1_target_y
                    self.skill1_phase = 'LANDING'
                    self.skill1_landing_timer = 0
                else:
                    # 계속 이동
                    ratio = move_distance / distance
                    self.x += dx * ratio
                    self.y += dy * ratio
            else:
                # 도착
                self.skill1_phase = 'LANDING'
                self.skill1_landing_timer = 0

        elif self.skill1_phase == 'LANDING':
            # 착지 모션: 1-6번 프레임 재생
            self.skill1_landing_timer += game_framework.frame_time
            motion_progress = self.skill1_landing_timer / self.skill1_landing_duration
            self.frame = min(int(motion_progress * 6) + 1, 6)  # 1-6 프레임

            if self.skill1_landing_timer >= self.skill1_landing_duration:
                # 스킬 종료
                self.is_using_skill = False
                self.current_skill = None
                self.skill1_phase = 'READY'
                self.state = 'IDLE'

    def get_skill1_effect_bb(self):
        """Skill1 돌진 궤적의 타격 범위 반환"""
        if self.current_skill != 'SKILL1' or self.skill1_phase != 'DASHING':
            return None

        # 시작점에서 현재 위치까지의 직사각형 범위
        min_x = min(self.skill1_start_x, self.x)
        max_x = max(self.skill1_start_x, self.x)
        min_y = min(self.skill1_start_y, self.y) - self.height / 2
        max_y = max(self.skill1_start_y, self.y) + self.height / 2

        return (min_x, min_y, max_x, max_y)

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
        self.skill1_phase = 'READY'  # 초기 단계로 설정
        self.frame_time = 0  # 프레임 타이머 초기화

        # 시작 위치 및 목표 위치 설정
        player = SKRR.get_player()
        if player:
            self.skill1_start_x = self.x
            self.skill1_start_y = self.y
            self.skill1_target_x = player.x
            self.skill1_target_y = player.y
        else:
            self.skill1_target_x = self.x
            self.skill1_target_y = self.y

        # 대쉬 속도 및 착지 시간 설정
        self.skill1_dash_speed = 500  # 대쉬 속도 (픽셀/초)
        self.skill1_landing_duration = 0.6  # 착지 모션 지속 시간 (초)

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
            if 'skill1_motion' in GrimReaper.images and GrimReaper.images['skill1_motion']:
                if self.frame < len(GrimReaper.images['skill1_motion']):
                    img = GrimReaper.images['skill1_motion'][self.frame]

        elif self.state == 'SKILL2':
            if 'skill2' in GrimReaper.images and GrimReaper.images['skill2']:
                img = GrimReaper.images['skill2'][self.frame % len(GrimReaper.images['skill2'])]

        # 보스 이미지 그리기
        if img:
            cam_x, cam_y = self.x, self.y
            if game_world.camera:
                cam_x, cam_y = game_world.camera.apply(self.x, self.y)

            if self.face_dir == 1:
                img.clip_draw(0, 0, img.w, img.h, cam_x, cam_y, img.w * self.scale, img.h * self.scale)
            else:
                img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', cam_x, cam_y, img.w * self.scale, img.h * self.scale)

        # Skill1 돌진 이펙트 그리기
        if self.state == 'SKILL1' and self.skill1_phase == 'DASHING':
            self.draw_skill1_effect()

        # 체력바 그리기
        # self.draw_hp_bar()

        # 충돌박스 그리기
        self.draw_collision_box()

    def draw_skill1_effect(self):
        """Skill1 돌진 궤적 이펙트 그리기"""
        if 'skill1_effect' not in GrimReaper.images or not GrimReaper.images['skill1_effect']:
            return

        # 시작점부터 현재 위치까지 이펙트 그리기
        dx = self.x - self.skill1_start_x
        dy = self.y - self.skill1_start_y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance < 10:
            return

        # 이펙트 애니메이션 프레임
        effect_frame = int(self.frame_time * 30.0) % len(GrimReaper.images['skill1_effect'])
        effect_img = GrimReaper.images['skill1_effect'][effect_frame]

        # 시작점과 현재점 사이에 이펙트 그리기
        segments = max(1, int(distance / 50))  # 50픽셀마다 이펙트

        for i in range(segments + 1):
            ratio = i / max(segments, 1)
            effect_x = self.skill1_start_x + dx * ratio
            effect_y = self.skill1_start_y + dy * ratio

            if game_world.camera:
                cam_x, cam_y = game_world.camera.apply(effect_x, effect_y)

                # 이펙트 그리기 (방향에 따라 회전)
                if self.face_dir == 1:
                    effect_img.clip_draw(0, 0, effect_img.w, effect_img.h,
                                       cam_x, cam_y,
                                       effect_img.w * 2, effect_img.h * 2)
                else:
                    effect_img.clip_composite_draw(0, 0, effect_img.w, effect_img.h,
                                                  0, 'h', cam_x, cam_y,
                                                  effect_img.w * 2, effect_img.h * 2)

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
