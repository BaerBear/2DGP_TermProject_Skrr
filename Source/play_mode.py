from pico2d import *
from ResourceManager import ResourceManager
import SKRR
from StageManager import StageManager
from Sound_Loader import SoundManager
from Camera import Camera
from TileMap import TileMap
import game_framework
import game_world
import Events
import os

Skrr = None
tile_map = None
show_collision_boxes = True  # 충돌 박스 표시 여부
current_stage = 0  # 현재 스테이지 (0: Stage0, 1: Stage1, 2: BossStage)

def init():
    global Skrr, tile_map, current_stage
    hide_lattice()

    ResourceManager.preload_resources()
    SoundManager.stop_bgm()
    SoundManager.play_bgm('chapter1', repeat=True)

    current_stage = 0
    tmx_path = os.path.join(os.path.dirname(__file__), '..', 'Tilemap_work', 'Stage0.tmx')
    tile_map = TileMap(tmx_path)

    Skrr = SKRR.SKRR()
    Skrr.set_tile_map(tile_map)

    camera = Camera.get_instance()
    camera.set_target(Skrr)
    camera.set_bounds(
        0,
        tile_map.map_width * tile_map.tile_width,
        0,
        tile_map.map_height * tile_map.tile_height
    )
    game_world.set_camera(camera)

    tile_map.set_camera(camera)

    # Layer 2: 플레이어
    game_world.add_object(Skrr, 2)

    game_world.add_collision_pair('player:tilemap', Skrr, tile_map)

    # 스테이지별 적 로드
    StageManager.load_stage_enemies(current_stage, Skrr, tile_map)

    # 플레이어 공격과 적의 충돌 쌍 등록
    game_world.add_collision_pair('player_attack:enemy', Skrr, None)


def load_stage(stage_num):
    global tile_map, current_stage

    stage_files = {
        0: 'Stage0.tmx',
        1: 'Stage1.tmx',
        2: 'BossStage.tmx'
    }
    Skrr.face_dir = 1
    if stage_num not in stage_files:
        return

    before_stage = current_stage
    current_stage = stage_num

    StageManager.clear_all_enemies()

    if tile_map:
        game_world.remove_collision_object(tile_map)

    tmx_path = os.path.join(os.path.dirname(__file__), '..', 'Tilemap_work', stage_files[stage_num])
    tile_map = TileMap(tmx_path)

    Skrr.set_tile_map(tile_map)

    # 카메라 범위 업데이트
    camera = Camera.get_instance()
    camera.set_bounds(
        0,
        tile_map.map_width * tile_map.tile_width,
        0,
        tile_map.map_height * tile_map.tile_height
    )

    tile_map.set_camera(camera)

    # 충돌 페어 재설정
    game_world.add_collision_pair('player:tilemap', Skrr, tile_map)

    start_x, start_y = SKRR.stage_start_positions[stage_num]
    Skrr.x = start_x
    Skrr.y = start_y

    StageManager.load_stage_enemies(stage_num, Skrr, tile_map)

    if before_stage == 2 and stage_num != 2:
        SoundManager.stop_bgm()
        SoundManager.play_bgm('chapter1', repeat=True)
    elif current_stage == 2:
        SoundManager.stop_bgm()
        SoundManager.play_bgm('chapter1_boss', repeat=True)

    print(f"Stage {stage_num} loaded: {stage_files[stage_num]} at position ({start_x}, {start_y})")

def finish():
    game_world.clear()


def check_attack_collision():
    """플레이어 공격과 적 충돌 체크"""
    player = SKRR.get_player()
    if not player:
        return

    hitbox = player.get_attack_hitbox()
    if hitbox is None:
        return

    enemy_layer = 1
    if enemy_layer >= len(game_world.world):
        return

    enemies = list(game_world.world[enemy_layer])

    hitbox_left, hitbox_bottom, hitbox_right, hitbox_top = hitbox

    for enemy in enemies:
        if not player.can_hit_target(enemy):
            continue

        # 적의 바운딩 박스 가져오기
        if not hasattr(enemy, 'get_bb'):
            continue

        try:
            enemy_bb = enemy.get_bb()
            enemy_left, enemy_bottom, enemy_right, enemy_top = enemy_bb
        except:
            continue

        # AABB 충돌 검사
        if (hitbox_left < enemy_right and
                hitbox_right > enemy_left and
                hitbox_bottom < enemy_top and
                hitbox_top > enemy_bottom):
            # 충돌 발생! 적에게 데미지 적용
            if hasattr(enemy, 'take_damage'):
                damage = player.active_hitbox.get('damage', player.attack_power)
                enemy.take_damage(damage, player.x)

                # 타격 기록 추가 (multi_hit일 때는 타임스탬프도 기록)
                player.add_hit_target(enemy)

                is_multi_hit = player.active_hitbox.get('multi_hit', False)
                hit_interval = player.active_hitbox.get('hit_interval', 0.0)
                print(f"플레이어 공격 적중! 데미지: {damage} (다중 히트: {is_multi_hit}, 간격: {hit_interval}초)")


def check_player_damage():
    # 적이 공격
    player = SKRR.get_player()
    if not player or player.is_invincible:
        return

    player_bb = player.get_bb()

    # 모든 적의 공격과 충돌 체크
    if 3 not in game_world.world:
        return
    for enemy in game_world.world[3]:
        if not hasattr(enemy, 'get_attack_hitbox'):
            continue

        enemy_hitbox = enemy.get_attack_hitbox()
        if enemy_hitbox is None:
            continue

        # AABB 충돌 검사
        if (enemy_hitbox['x'] < player_bb[2] and
                enemy_hitbox['x'] + enemy_hitbox['width'] > player_bb[0] and
                enemy_hitbox['y'] < player_bb[3] and
                enemy_hitbox['y'] + enemy_hitbox['height'] > player_bb[1]):
            # 플레이어 피격
            player.get_damage(enemy_hitbox['damage'])


def update():
    game_world.update()
    game_world.handle_collision()
    if tile_map:
        tile_map.update()
    check_attack_collision()
    check_player_damage()

def draw():
    clear_canvas()
    if tile_map:
        tile_map.draw()

    game_world.render()

    if tile_map and show_collision_boxes:
        tile_map.draw_collision_boxes()

    update_canvas()

def handle_events():
    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN and e.key == SDLK_ESCAPE:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN and e.key == SDLK_F1:
            # F1 - 충돌 박스 표시 토글
            global show_collision_boxes
            show_collision_boxes = not show_collision_boxes
            SKRR.show_collision_box = show_collision_boxes
            print(f"Collision boxes: {'ON' if show_collision_boxes else 'OFF'}")
        elif e.type == SDL_KEYDOWN and e.key == SDLK_F2:
            # F2 - Stage0 로드
            load_stage(0)
        elif e.type == SDL_KEYDOWN and e.key == SDLK_F3:
            # F3 - Stage1 로드
            load_stage(1)
        elif e.type == SDL_KEYDOWN and e.key == SDLK_F4:
            # F4 - BossStage 로드
            load_stage(2)
        elif e.type == SDL_MOUSEBUTTONDOWN and e.button == SDL_BUTTON_LEFT:
            print(f"Mouse Left Click: ({e.x}, {get_canvas_height() - e.y})")
        elif e.type == SDL_KEYDOWN:
            Events.handle_key_down(e, Skrr)
        elif e.type == SDL_KEYUP:
            Events.handle_key_up(e, Skrr)

def pause():
    pass

def resume():
    pass
