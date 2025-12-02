from pico2d import *
from Enemy import Enemy
from ResourceManager import ResourceManager
import SKRR
import game_framework
import game_world

# 물리 상수 정의 (SKRR와 동일한 체계)
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel = 30 cm
GRAVITY_MULTIPLIER = 5.0
BASE_GRAVITY = 9.8
GRAVITY = BASE_GRAVITY * GRAVITY_MULTIPLIER

# 보스 이동 속도 (KMPH -> PPS 변환)
BOSS_WALK_SPEED_KMPH = 15.0  # 시속 15km
BOSS_WALK_SPEED_MPM = (BOSS_WALK_SPEED_KMPH * 1000.0 / 60.0)  # 분당 미터
BOSS_WALK_SPEED_MPS = (BOSS_WALK_SPEED_MPM / 60.0)  # 초당 미터
BOSS_WALK_SPEED_PPS = (BOSS_WALK_SPEED_MPS * PIXEL_PER_METER)  # 초당 픽셀

# 보스 대쉬 속도
BOSS_DASH_SPEED_KMPH = 60.0  # 시속 60km
BOSS_DASH_SPEED_MPM = (BOSS_DASH_SPEED_KMPH * 1000.0 / 60.0)
BOSS_DASH_SPEED_MPS = (BOSS_DASH_SPEED_MPM / 60.0)
BOSS_DASH_SPEED_PPS = (BOSS_DASH_SPEED_MPS * PIXEL_PER_METER)

# 스킬1 돌진 속도
SKILL1_DASH_SPEED_KMPH = 100.0  # 시속 100km (매우 빠름)
SKILL1_DASH_SPEED_MPM = (SKILL1_DASH_SPEED_KMPH * 1000.0 / 60.0)
SKILL1_DASH_SPEED_MPS = (SKILL1_DASH_SPEED_MPM / 60.0)
SKILL1_DASH_SPEED_PPS = (SKILL1_DASH_SPEED_MPS * PIXEL_PER_METER)

# 거리 상수 (미터 단위로 정의)
DETECT_RANGE_METER = 21.0  # 21미터
DETECT_RANGE_PPS = DETECT_RANGE_METER * PIXEL_PER_METER

SKILL_RANGE_METER = 15.0  # 15미터
SKILL_RANGE_PPS = SKILL_RANGE_METER * PIXEL_PER_METER

DASH_RANGE_MIN_METER = 6.0  # 6미터
DASH_RANGE_MIN_PPS = DASH_RANGE_MIN_METER * PIXEL_PER_METER
DASH_RANGE_MAX_METER = 15.0  # 15미터
DASH_RANGE_MAX_PPS = DASH_RANGE_MAX_METER * PIXEL_PER_METER

ATTACK_RANGE_METER = 4.5  # 4.5미터
ATTACK_RANGE_PPS = ATTACK_RANGE_METER * PIXEL_PER_METER

DASH_DISTANCE_METER = 15.0  # 대쉬 거리 15미터
DASH_DISTANCE_PPS = DASH_DISTANCE_METER * PIXEL_PER_METER

# 프레임 애니메이션 상수
IDLE_TIME_PER_ACTION = 0.167  # 약 6 FPS
IDLE_ACTION_PER_TIME = 1.0 / IDLE_TIME_PER_ACTION
IDLE_FRAMES_PER_ACTION = 10

WALK_TIME_PER_ACTION = 0.125  # 약 8 FPS
WALK_ACTION_PER_TIME = 1.0 / WALK_TIME_PER_ACTION
WALK_FRAMES_PER_ACTION = 8

ATTACK_TIME_PER_ACTION = 0.1  # 10 FPS
ATTACK_ACTION_PER_TIME = 1.0 / ATTACK_TIME_PER_ACTION
ATTACK_FRAMES_PER_ACTION = 10

SKILL1_READY_TIME = 0.1  # 준비 시간
SKILL1_LANDING_TIME = 0.7  # 착지 모션 시간
SKILL1_LANDING_FRAMES = 7  # 착지 프레임 수

SKILL2_TIME_PER_ACTION = 0.1  # 10 FPS
SKILL2_ACTION_PER_TIME = 1.0 / SKILL2_TIME_PER_ACTION

class GrimReaper(Enemy):
    images = None
    skill1_effect = None  # 스킬1 이펙트 이미지 추가

    def __init__(self, x, y):
        super().__init__(x, y)

        # 보스 기본 스탯
        self.hp = 2000
        self.max_hp = 2000
        self.scale = 3

        # 이동 속도 (물리 기반)
        self.walk_speed = BOSS_WALK_SPEED_PPS
        self.dash_speed = BOSS_DASH_SPEED_PPS
        self.skill1_dash_speed = SKILL1_DASH_SPEED_PPS

        # 대쉬 상태
        self.is_dashing = False
        self.dash_distance = DASH_DISTANCE_PPS
        self.dash_traveled = 0

        # 스킬 쿨다운 (초 단위)
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
        self.skill1_landing_timer = 0
        self.skill1_ready_timer = 0
        self.skill1_effect_timer = 0  # 이펙트 애니메이션용 타이머

        # 이미지 로드
        if not GrimReaper.images:
            GrimReaper.images = ResourceManager.get_boss_images('GrimReaper')
            GrimReaper.skill1_effect = GrimReaper.images.get('skill1_effect', [])


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
                self.update_skill1()
            elif self.current_skill == 'SKILL2':
                self.update_skill2()

        # 일반 행동 패턴
        else:
            # 스킬 우선순위 체크
            if self.dis_to_player <= SKILL_RANGE_PPS:
                # Skill1 사용 가능?
                if current_time - self.skill1_last_use >= self.skill1_cooldown:
                    self.use_skill1()
                    return
                # Skill2 사용 가능?
                elif current_time - self.skill2_last_use >= self.skill2_cooldown:
                    self.use_skill2()
                    return

            # 대쉬 공격 (중거리)
            if DASH_RANGE_MIN_PPS <= self.dis_to_player <= DASH_RANGE_MAX_PPS:
                if current_time - self.dash_last_use >= self.dash_cooldown:
                    self.start_dash()
                    return

            # 기본 공격 (근거리)
            if self.dis_to_player <= ATTACK_RANGE_PPS:
                if current_time - self.attack_last_use_time >= self.attack_cooldown_time:
                    self.state = 'ATTACK'
                    self.is_attacking = True
                    self.attack_last_use_time = current_time
                elif not self.is_attacking:
                    self.state = 'IDLE'

            # 이동
            elif self.dis_to_player <= DETECT_RANGE_PPS:
                self.state = 'WALK'
                self.x += self.walk_speed * self.face_dir * game_framework.frame_time

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
            attack_duration = len(GrimReaper.images.get('attack', [])) * ATTACK_TIME_PER_ACTION
            if self.frame_time >= attack_duration:
                self.is_attacking = False

    def update_frame(self):
        """프레임 업데이트 (물리 기반 시간 계산)"""
        if self.state == 'IDLE':
            frame_count = len(GrimReaper.images.get('idle', []))
            if frame_count > 0:
                self.frame = int(self.frame_time * IDLE_ACTION_PER_TIME) % frame_count

        elif self.state == 'WALK' or self.state == 'DASH':
            frame_count = len(GrimReaper.images.get('walk', []))
            if frame_count > 0:
                self.frame = int(self.frame_time * WALK_ACTION_PER_TIME) % frame_count

        elif self.state == 'ATTACK':
            frame_count = len(GrimReaper.images.get('attack', []))
            if frame_count > 0:
                self.frame = int(self.frame_time * ATTACK_ACTION_PER_TIME) % frame_count

        elif self.state == 'SKILL1':
            # Skill1은 별도로 처리 (단계별로 다름)
            pass

        elif self.state == 'SKILL2':
            frame_count = len(GrimReaper.images.get('skill2', []))
            if frame_count > 0:
                self.frame = int(self.frame_time * SKILL2_ACTION_PER_TIME) % frame_count

    def update_skill1(self):
        """Skill1 (고속 돌진) 업데이트 - 물리 기반"""
        if self.skill1_phase == 'READY':
            # 준비 단계: 0번 모션 유지
            self.frame = 0
            self.skill1_ready_timer += game_framework.frame_time

            # 준비 시간이 지나면 돌진 시작
            if self.skill1_ready_timer >= SKILL1_READY_TIME:
                self.skill1_phase = 'DASHING'
                self.skill1_ready_timer = 0
                self.skill1_effect_timer = 0  # 이펙트 타이머 초기화

        elif self.skill1_phase == 'DASHING':
            # 이펙트 타이머 업데이트
            self.skill1_effect_timer += game_framework.frame_time

            # 돌진 중: 목표 지점까지 고속 이동 (물리 기반 속도)
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
            # 착지 모션: 1-6번 프레임 재생 (물리 기반 타이밍)
            self.skill1_landing_timer += game_framework.frame_time
            motion_progress = self.skill1_landing_timer / SKILL1_LANDING_TIME
            self.frame = min(int(motion_progress * (SKILL1_LANDING_FRAMES - 1)) + 1, SKILL1_LANDING_FRAMES - 1)

            if self.skill1_landing_timer >= SKILL1_LANDING_TIME:
                # 스킬 종료
                self.is_using_skill = False
                self.current_skill = None
                self.skill1_phase = 'READY'
                self.state = 'IDLE'

    def update_skill2(self):
        """Skill2 업데이트 - 물리 기반"""
        skill_duration = len(GrimReaper.images.get('skill2', [])) * SKILL2_TIME_PER_ACTION
        if self.frame_time >= skill_duration:
            self.is_using_skill = False
            self.current_skill = None
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
        self.skill1_phase = 'READY'
        self.skill1_ready_timer = 0
        self.frame_time = 0

        # 시작 위치 및 목표 위치 설정
        player = SKRR.get_player()
        if player:
            self.skill1_start_x = self.x
            self.skill1_start_y = self.y
            self.skill1_target_x = player.x
            self.skill1_target_y = self.y
        else:
            self.skill1_target_x = self.x
            self.skill1_target_y = self.y

    def use_skill2(self):
        """스킬2 사용"""
        self.is_using_skill = True
        self.current_skill = 'SKILL2'
        self.state = 'SKILL2'
        self.skill2_last_use = get_time()
        self.frame_time = 0

    def draw(self):
        if not self.is_alive:
            return

        if not GrimReaper.images:
            return

        # 현재 상태에 맞는 이미지 가져오기
        current_images = None
        if self.state == 'IDLE':
            current_images = GrimReaper.images.get('idle', [])
        elif self.state == 'WALK':
            current_images = GrimReaper.images.get('walk', [])
        elif self.state == 'ATTACK':
            current_images = GrimReaper.images.get('attack', [])
        elif self.state == 'DASH':
            current_images = GrimReaper.images.get('walk', [])
        elif self.state == 'SKILL1':
            current_images = GrimReaper.images.get('skill1_motion', [])
        elif self.state == 'SKILL2':
            current_images = GrimReaper.images.get('skill2', [])

        if current_images and len(current_images) > 0:
            frame_index = min(self.frame, len(current_images) - 1)
            img = current_images[frame_index]

            cam_x, cam_y = self.x, self.y
            if game_world.camera:
                cam_x, cam_y = game_world.camera.apply(self.x, self.y)

            if self.face_dir == -1:
                img.clip_composite_draw(0, 0, img.w, img.h, 0, 'h', cam_x, cam_y, img.w * self.scale, img.h * self.scale)
            else:
                img.clip_draw(0, 0, img.w, img.h, cam_x, cam_y, img.w * self.scale, img.h * self.scale)

        if self.current_skill == 'SKILL1' and self.skill1_phase == 'DASHING' and GrimReaper.images:
            effect_images = GrimReaper.images.get('skill1_effect', [])
            if effect_images and len(effect_images) > 0:
                effect_count = len(effect_images)
                effect_fps = 32
                effect_frame = int(self.skill1_effect_timer * effect_fps) % effect_count
                effect_img = effect_images[effect_frame]

                center_x = (self.skill1_start_x + self.skill1_target_x) / 2
                center_y = (self.skill1_start_y + self.skill1_target_y) / 2

                cam_x, cam_y = center_x, center_y
                if game_world.camera:
                    cam_x, cam_y = game_world.camera.apply(center_x, center_y)

                effect_img.draw(cam_x, cam_y, effect_img.w * 2, effect_img.h* 2)

        # 디버그용 충돌 박스 그리기
        if SKRR.SKRR.show_collision_box:
            from pico2d import draw_rectangle
            if game_world.camera:
                camera_x, camera_y = game_world.camera.get_position()
                left, bottom, right, top = self.get_bb()
                draw_rectangle(left - camera_x, bottom - camera_y,
                               right - camera_x, top - camera_y)

                hit_left, hit_bottom, hit_right, hit_top = self.get_hit_bb()
                draw_rectangle(hit_left - camera_x, hit_bottom - camera_y,
                               hit_right - camera_x, hit_top - camera_y)
