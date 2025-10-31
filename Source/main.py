from pico2d import *
from SKRR import *
from Enemy import Knight_Sword, Knight_Bow, Knight_Tackle
from Sound_Loader import SoundManager
import Events
import game_world

def reset_world():
    SoundManager.initialize()
    SoundManager.play_bgm('chapter1', repeat=True)

    global Skrr
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

def update_world():
    game_world.update()

def render_world():
    clear_canvas()
    game_world.render()
    update_canvas()

running = True

open_canvas(1440, 900)

reset_world()

# game loop
while running:
    running = Events.handle_events(running, Skrr)
    update_world()
    render_world()
    delay(0.01)

close_canvas()