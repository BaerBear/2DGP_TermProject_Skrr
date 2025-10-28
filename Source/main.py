from pico2d import *
from SKRR import *
from Enemy import Knight_Sword, Knight_Bow, Knight_Tackle
from Sound_Loader import SoundManager
import Game_World
import Events

def reset_world():
    SoundManager.initialize()
    SoundManager.play_bgm('chapter1', repeat=True)

    global Skrr
    Skrr = SKRR()
    Game_World.add_object(Skrr, 2)

    # 테스트용 몬스터 생성
    tackle_knight = Knight_Tackle(1300, get_canvas_height() // 2)
    tackle_knight.target = Skrr
    Game_World.add_object(tackle_knight, 1)

    sword_knight = Knight_Sword(1000, get_canvas_height() // 2)
    sword_knight.target = Skrr
    Game_World.add_object(sword_knight, 1)

    bow_knight = Knight_Bow(1100, get_canvas_height() // 2)
    bow_knight.target = Skrr
    Game_World.add_object(bow_knight, 1)



def update_world():
    Game_World.update()

def render_world():
    clear_canvas()
    Game_World.render()
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