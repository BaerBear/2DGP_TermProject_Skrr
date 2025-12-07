import random

from pico2d import *
from Enemy import Enemy
from ResourceManager import ResourceManager
from Sound_Loader import SoundManager
from BossSkill import FireField
import SKRR
import game_framework
import game_world
from Gold import Gold

PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel = 30 cm
GRAVITY_MULTIPLIER = 5.0
BASE_GRAVITY = 9.8
GRAVITY = BASE_GRAVITY * GRAVITY_MULTIPLIER

# 보스 걷기 속도
BOSS_WALK_SPEED_KMPH = 15.0
BOSS_WALK_SPEED_MPM = (BOSS_WALK_SPEED_KMPH * 1000.0 / 60.0)
BOSS_WALK_SPEED_MPS = (BOSS_WALK_SPEED_MPM / 60.0)
BOSS_WALK_SPEED_PPS = (BOSS_WALK_SPEED_MPS * PIXEL_PER_METER)

# 보스 대쉬 속도
BOSS_DASH_SPEED_KMPH = 60.0
BOSS_DASH_SPEED_MPM = (BOSS_DASH_SPEED_KMPH * 1000.0 / 60.0)
BOSS_DASH_SPEED_MPS = (BOSS_DASH_SPEED_MPM / 60.0)
BOSS_DASH_SPEED_PPS = (BOSS_DASH_SPEED_MPS * PIXEL_PER_METER)

# 스킬1 돌진 속도
SKILL1_DASH_SPEED_KMPH = 100.0
SKILL1_DASH_SPEED_MPM = (SKILL1_DASH_SPEED_KMPH * 1000.0 / 60.0)
SKILL1_DASH_SPEED_MPS = (SKILL1_DASH_SPEED_MPM / 60.0)
SKILL1_DASH_SPEED_PPS = (SKILL1_DASH_SPEED_MPS * PIXEL_PER_METER)

# 거리 상수
DETECT_RANGE_METER = 21.0
DETECT_RANGE_PPS = DETECT_RANGE_METER * PIXEL_PER_METER

SKILL_RANGE_METER = 15.0
SKILL_RANGE_PPS = SKILL_RANGE_METER * PIXEL_PER_METER

DASH_RANGE_MIN_METER = 6.0
DASH_RANGE_MIN_PPS = DASH_RANGE_MIN_METER * PIXEL_PER_METER
DASH_RANGE_MAX_METER = 15.0
DASH_RANGE_MAX_PPS = DASH_RANGE_MAX_METER * PIXEL_PER_METER

ATTACK_RANGE_METER = 4.5
ATTACK_RANGE_PPS = ATTACK_RANGE_METER * PIXEL_PER_METER

DASH_DISTANCE_METER = 15.0
DASH_DISTANCE_PPS = DASH_DISTANCE_METER * PIXEL_PER_METER

# 프레임 애니메이션
IDLE_TIME_PER_ACTION = 0.167
IDLE_ACTION_PER_TIME = 1.0 / IDLE_TIME_PER_ACTION
IDLE_FRAMES_PER_ACTION = 10

WALK_TIME_PER_ACTION = 0.125
WALK_ACTION_PER_TIME = 1.0 / WALK_TIME_PER_ACTION
WALK_FRAMES_PER_ACTION = 8

ATTACK_TIME_PER_ACTION = 0.1
ATTACK_ACTION_PER_TIME = 1.0 / ATTACK_TIME_PER_ACTION
ATTACK_FRAMES_PER_ACTION = 10

SKILL1_READY_TIME = 0.1
SKILL1_LANDING_TIME = 0.7
SKILL1_LANDING_FRAMES = 7

SKILL2_TIME_PER_ACTION = 0.15
SKILL2_ACTION_PER_TIME = 1.0 / SKILL2_TIME_PER_ACTION

class GrimReaper(Enemy):
    images = None
    skill1_effect = None  # 스킬1 이펙트 이미지 추가

    def __init__(self, x, y):
        super().__init__(x, y)

        self.max_hp = 1000
        self.current_hp = self.max_hp
        self.scale = 2.5

        # 데미지
        self.basic_attack_damage = 30
        self.skill1_damage = 30

        self.walk_speed = BOSS_WALK_SPEED_PPS
        self.dash_speed = BOSS_DASH_SPEED_PPS
        self.skill1_dash_speed = SKILL1_DASH_SPEED_PPS

        self.is_dashing = False
        self.dash_distance = DASH_DISTANCE_PPS
        self.dash_traveled = 0

        self.skill1_cooldown = 15.0
        self.skill1_last_use = -15.0
        self.skill2_cooldown = 12.0
        self.skill2_last_use = -12.0
        self.dash_cooldown = 6.0
        self.dash_last_use = -6.0

        self.is_using_skill = False
        self.current_skill = None

        self.action_delay = 2.0  # 행동 간격
        self.last_action_time = -1.0

        self.skill1_phase = 'READY'
        self.skill1_start_x = 0
        self.skill1_start_y = 0
        self.skill1_target_x = 0
        self.skill1_target_y = 0
        self.skill1_landing_timer = 0
        self.skill1_ready_timer = 0
        self.skill1_effect_timer = 0

        if not GrimReaper.images:
            GrimReaper.images = ResourceManager.get_boss_images('GrimReaper')
            GrimReaper.skill1_effect = GrimReaper.images.get('skill1_effect', [])


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

    def take_damage(self, damage, attacker_x):
        if self.current_hp <= 0:
            return False

        actual_damage = int(damage * (100 / (100 + self.defense)))
        damage_variation = max(1, random.randint(actual_damage - int(actual_damage * 0.2),
                                                 actual_damage + int(actual_damage * 0.2)))
        self.current_hp -= damage_variation
        print(f'Boss took {damage_variation} damage, current HP: {self.current_hp}/{self.max_hp}')

        if self.current_hp <= 0:
            self.on_death()
            return True

        return True

    def on_death(self):
        self.is_alive = False
        SoundManager.play_enemy_sound('enemy_big_dead')

        gold_amount = random.randint(50, 100)
        gold = Gold(self.x, self.y, gold_amount)
        gold.set_tile_map(self.tile_map)
        game_world.add_object(gold, 1)

        game_world.remove_object(self)

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

        if not self.is_using_skill and not self.is_dashing and not self.is_attacking:
            if player.x > self.x:
                self.face_dir = 1
            else:
                self.face_dir = -1

        if self.is_dashing:
            self.state = 'DASH'
            move_distance = self.dash_speed * game_framework.frame_time
            self.x += move_distance * self.face_dir
            self.dash_traveled += move_distance

            if self.dash_traveled >= self.dash_distance:
                self.is_dashing = False
                self.dash_traveled = 0
                self.state = 'IDLE'

        elif self.is_using_skill:
            if self.current_skill == 'SKILL1':
                self.update_skill1()
            elif self.current_skill == 'SKILL2':
                self.update_skill2()

        elif self.is_attacking:
            self.state = 'ATTACK'

        elif self.dis_to_player <= DETECT_RANGE_PPS:
            if current_time - self.last_action_time < self.action_delay:
                if self.dis_to_player >= ATTACK_RANGE_PPS:
                    self.state = 'WALK'
                    self.x += self.walk_speed * self.face_dir * game_framework.frame_time
                else:
                    self.state = 'IDLE'
            else:
                if self.dis_to_player <= SKILL_RANGE_PPS:
                    if current_time - self.skill1_last_use >= self.skill1_cooldown:
                        self.use_skill1()
                        SoundManager.play_enemy_sound('boss_skill1')
                        self.set_attack_hitbox(
                            width=250,
                            height=self.height * 1.2,
                            center_offset_x= 100,
                            center_offset_y=0,
                            damage=self.skill1_damage,
                            multi_hit=False
                        )
                        return
                    elif current_time - self.skill2_last_use >= self.skill2_cooldown:
                        self.use_skill2()
                        SoundManager.play_enemy_sound('boss_skill2')
                        return

                if DASH_RANGE_MIN_PPS <= self.dis_to_player <= DASH_RANGE_MAX_PPS:
                    if current_time - self.dash_last_use >= self.dash_cooldown:
                        self.start_dash()
                        return

                if self.dis_to_player <= ATTACK_RANGE_PPS:
                    if current_time - self.attack_last_use_time >= self.attack_cooldown_time:
                        SoundManager.play_enemy_sound('boss_attack')
                        self.state = 'ATTACK'
                        self.is_attacking = True
                        self.attack_last_use_time = current_time
                    else:
                        self.state = 'IDLE'
                else:
                    self.state = 'WALK'
                    self.x += self.walk_speed * self.face_dir * game_framework.frame_time
        else:
            # 감지 범위 밖이면 IDLE
            self.state = 'IDLE'

        # 일반 상태의 맵 경계 체크 (스킬1은 위에서 이미 처리됨)
        if self.tile_map and not (self.is_using_skill and self.current_skill == 'SKILL1'):
            map_width_pixels = self.tile_map.map_width * self.tile_map.tile_width
            hit_boundary = False

            if self.x < self.width / 2:
                self.x = self.width / 2
                hit_boundary = True
            elif self.x > map_width_pixels - self.width / 2:
                self.x = map_width_pixels - self.width / 2
                hit_boundary = True

            # 경계에 닿았을 때 행동 중단
            if hit_boundary:
                if self.is_dashing:
                    self.is_dashing = False
                    self.dash_traveled = 0
                    self.state = 'IDLE'
                    self.clear_attack_hitbox()
                    self.last_action_time = get_time()

        if self.state != self.prev_state:
            self.frame_time = 0
            self.prev_state = self.state

        self.frame_time += game_framework.frame_time

        self.update_frame()

        if self.state == 'ATTACK' and self.is_attacking:
            # 공격 프레임 중에만 히트박스 활성화
            if 4 <= self.frame < 6:
                self.set_attack_hitbox(
                    width=200,
                    height=self.height * 1.1,
                    center_offset_x=75,
                    center_offset_y=0,
                    damage=self.basic_attack_damage,
                    multi_hit=False
                )
                self.get_attack_hitbox()
            else:
                self.attack_bounding_box = None

            attack_duration = len(GrimReaper.images.get('attack', [])) * ATTACK_TIME_PER_ACTION
            if self.frame_time >= attack_duration:
                self.is_attacking = False
                self.clear_attack_hitbox()
                self.last_action_time = current_time

    def update_frame(self):
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
            pass

        elif self.state == 'SKILL2':
            frame_count = len(GrimReaper.images.get('skill2_motion', []))
            if frame_count > 0:
                self.frame = int(self.frame_time * SKILL2_ACTION_PER_TIME) % frame_count

    def update_skill1(self):
        """Skill1 (고속 돌진) 업데이트 - 물리 기반"""
        if self.skill1_phase == 'READY':
            # 준비 단계: 0번 모션 유지
            self.frame = 0
            self.skill1_ready_timer += game_framework.frame_time
            self.get_attack_hitbox()

            # 준비 시간이 지나면 돌진 시작
            if self.skill1_ready_timer >= SKILL1_READY_TIME:
                self.skill1_phase = 'DASHING'
                self.skill1_ready_timer = 0
                self.skill1_effect_timer = 0  # 이펙트 타이머 초기화
                print(f"[SKILL1] Phase: READY -> DASHING")

        elif self.skill1_phase == 'DASHING':
            # 이펙트 타이머 업데이트
            self.skill1_effect_timer += game_framework.frame_time

            # 돌진 중 히트박스 활성화
            self.get_attack_hitbox()

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
                    self.clear_attack_hitbox()
                    print(f"[SKILL1] Phase: DASHING -> LANDING (도착)")
                else:
                    # 다음 위치 계산
                    ratio = move_distance / distance
                    next_x = self.x + dx * ratio
                    next_y = self.y + dy * ratio

                    # 타일 충돌 체크: 다음 위치에서 충돌하는지 확인
                    can_move = True
                    if self.tile_map:
                        # 다음 위치의 바운딩 박스 계산
                        next_left = next_x - self.width / 2
                        next_bottom = next_y - self.height / 2
                        next_right = next_x + self.width / 2
                        next_top = next_y + self.height / 2

                        # 타일 충돌 체크
                        colliding_tiles = self.tile_map.check_collision(next_left, next_bottom, next_right, next_top)

                        # 벽 타일(tile 레이어)과 충돌하는지 확인
                        for tile in colliding_tiles:
                            if tile['layer'] == 'tile':
                                # 타일의 경계
                                tile_left = tile['left']
                                tile_right = tile['right']
                                tile_bottom = tile['bottom']
                                tile_top = tile['top']

                                # 현재 위치의 바운딩 박스
                                current_bottom = self.y - self.height / 2
                                current_top = self.y + self.height / 2
                                current_left = self.x - self.width / 2
                                current_right = self.x + self.width / 2

                                # y축 겹침 확인
                                y_overlap = not (current_top < tile_bottom or current_bottom > tile_top)

                                if y_overlap:
                                    # 오른쪽으로 이동 중 타일의 왼쪽 벽에 충돌
                                    if self.face_dir == 1 and current_right <= tile_left and next_right > tile_left:
                                        can_move = False
                                        self.x = tile_left - self.width / 2 - 1
                                        print(f"[SKILL1] 타일 충돌 감지 (오른쪽 이동, 벽 x={tile_left})")
                                        break
                                    # 왼쪽으로 이동 중 타일의 오른쪽 벽에 충돌
                                    elif self.face_dir == -1 and current_left >= tile_right and next_left < tile_right:
                                        can_move = False
                                        self.x = tile_right + self.width / 2 + 1
                                        print(f"[SKILL1] 타일 충돌 감지 (왼쪽 이동, 벽 x={tile_right})")
                                        break

                        # 맵 경계 체크
                        if can_move and self.tile_map:
                            map_width_pixels = self.tile_map.map_width * self.tile_map.tile_width

                            if self.face_dir == 1:
                                if next_right >= map_width_pixels - 5:
                                    can_move = False
                                    self.x = map_width_pixels - self.width / 2 - 5
                                    print(f"[SKILL1] 맵 경계 충돌 (오른쪽)")
                            else:
                                if next_left <= 5:
                                    can_move = False
                                    self.x = self.width / 2 + 5
                                    print(f"[SKILL1] 맵 경계 충돌 (왼쪽)")

                    if can_move:
                        # 이동 가능하면 계속 이동
                        self.x = next_x
                        self.y = next_y
                    else:
                        # 벽/타일에 도달하면 즉시 착지
                        self.skill1_phase = 'LANDING'
                        self.skill1_landing_timer = 0
                        self.clear_attack_hitbox()
                        print(f"[SKILL1] Phase: DASHING -> LANDING (벽/타일 도달)")
            else:
                # 도착
                self.skill1_phase = 'LANDING'
                self.skill1_landing_timer = 0
                self.clear_attack_hitbox()
                print(f"[SKILL1] Phase: DASHING -> LANDING (거리 10 이하)")

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
                self.last_action_time = get_time()
                print(f"[SKILL1] Phase: LANDING -> IDLE (스킬 완료)")

    def update_skill2(self):
        """Skill2 업데이트 - 물리 기반"""
        skill_duration = len(GrimReaper.images.get('skill2_motion', [])) * SKILL2_TIME_PER_ACTION
        if self.frame_time >= skill_duration:
            self.is_using_skill = False
            self.current_skill = None
            self.state = 'IDLE'
            self.last_action_time = get_time()  # 스킬 후 행동 간격 시작

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

        player = SKRR.get_player()
        self.skill1_start_x = self.x
        self.skill1_start_y = self.y
        self.skill1_target_x = self.x + int(500 * self.face_dir)
        self.skill1_target_y = self.y

    def use_skill2(self):
        """스킬2 사용"""
        self.is_using_skill = True
        self.current_skill = 'SKILL2'
        self.state = 'SKILL2'
        self.skill2_last_use = get_time()
        self.frame_time = 0

        fire_field = FireField(self.x, self.y, GrimReaper.images)
        game_world.add_object(fire_field, 2)

    def draw(self):
        if not self.is_alive:
            return

        if not GrimReaper.images:
            return

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
            current_images = GrimReaper.images.get('skill2_motion', [])

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
                effect_fps = 12
                effect_frame = int(self.skill1_effect_timer * effect_fps) % effect_count
                effect_img = effect_images[effect_frame]

                center_x = (self.skill1_start_x + self.skill1_target_x) / 2
                center_y = (self.skill1_start_y + self.skill1_target_y) / 2

                cam_x, cam_y = center_x, center_y
                if game_world.camera:
                    cam_x, cam_y = game_world.camera.apply(center_x, center_y)

                effect_img.draw(cam_x, cam_y, effect_img.w * 2, effect_img.h* 2)

        if game_framework.show_collision_boxes:
            from pico2d import draw_rectangle
            if game_world.camera:
                camera_x, camera_y = game_world.camera.get_position()
                left, bottom, right, top = self.get_bb()
                draw_rectangle(left - camera_x, bottom - camera_y,
                               right - camera_x, top - camera_y)

                # 공격 히트박스도 그리기
                hitbox = self.attack_bounding_box
                if hitbox:
                    draw_rectangle(hitbox[0] - camera_x, hitbox[1] - camera_y,
                                   hitbox[2] - camera_x, hitbox[3] - camera_y)
