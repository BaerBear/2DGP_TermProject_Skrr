from pico2d import *
from ResourceManager import ResourceManager
from SKRR import SKRR
from Enemy import Knight_Sword, Knight_Bow, Knight_Tackle
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

def init():
    global Skrr, tile_map

    ResourceManager.preload_resources()

    SoundManager.initialize()
    SoundManager.play_bgm('chapter1', repeat=True)

    tmx_path = os.path.join(os.path.dirname(__file__), '..', 'Tilemap_work', 'Stage1.tmx')
    tile_map = TileMap(tmx_path)

    Skrr = SKRR()
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

    # Layer 1: 적(Enemy)
    sword_knight = Knight_Sword(900, get_canvas_height() // 2)
    sword_knight.target = Skrr
    game_world.add_object(sword_knight, 1)

    bow_knight = Knight_Bow(1100, get_canvas_height() // 2)
    bow_knight.target = Skrr
    game_world.add_object(bow_knight, 1)

    tackle_knight = Knight_Tackle(700, get_canvas_height() // 2)
    tackle_knight.target = Skrr
    game_world.add_object(tackle_knight, 1)

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
            # F1 키로 충돌 박스 표시 토글
            global show_collision_boxes
            show_collision_boxes = not show_collision_boxes
        elif e.type == SDL_KEYDOWN:
            Events.handle_key_down(e, Skrr)
        elif e.type == SDL_KEYUP:
            Events.handle_key_up(e, Skrr)

def pause():
    pass

def resume():
    pass
