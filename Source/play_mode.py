from pico2d import *
from SKRR import SKRR
from Enemy import Knight_Sword, Knight_Bow, Knight_Tackle
from Sound_Loader import SoundManager
import game_framework
import game_world
import Events

Skrr = None

def init():
    global Skrr

    SoundManager.initialize()
    SoundManager.play_bgm('chapter1', repeat=True)

    Skrr = SKRR()

    # Layer 2: 플레이어
    game_world.add_object(Skrr, 2)

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

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def handle_events():
    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN and e.key == SDLK_ESCAPE:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN:
            Events.handle_key_down(e, Skrr)
        elif e.type == SDL_KEYUP:
            Events.handle_key_up(e, Skrr)

def pause():
    pass

def resume():
    pass
