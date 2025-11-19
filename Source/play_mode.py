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

    SoundManager.initialize()
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

    # 스테이지별 적 로드 (StageManager 사용)
    StageManager.load_stage_enemies(current_stage, Skrr)


def load_stage(stage_num):
    global tile_map, current_stage

    stage_files = {
        0: 'Stage0.tmx',
        1: 'Stage1.tmx',
        2: 'BossStage.tmx'
    }

    if stage_num not in stage_files:
        return

    current_stage = stage_num

    StageManager.clear_all_enemies()

    # 기존 타일맵 제거
    if tile_map:
        game_world.remove_collision_object(tile_map)

    # 새 타일맵 로드
    tmx_path = os.path.join(os.path.dirname(__file__), '..', 'Tilemap_work', stage_files[stage_num])
    tile_map = TileMap(tmx_path)

    # 플레이어에 타일맵 설정
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

    StageManager.load_stage_enemies(stage_num, Skrr)

    print(f"Stage {stage_num} loaded: {stage_files[stage_num]} at position ({start_x}, {start_y})")

def finish():
    game_world.clear()

def update():
    game_world.update()
    game_world.handle_collision()
    if tile_map:
        tile_map.update()

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
        elif e.type == SDL_KEYDOWN:
            Events.handle_key_down(e, Skrr)
        elif e.type == SDL_KEYUP:
            Events.handle_key_up(e, Skrr)

def pause():
    pass

def resume():
    pass
