from pico2d import *
from SKRR import *
from Enemy import Knight_Sword, Knight_Bow, Knight_Tackle
import Events

def reset_world():
    global world, enemies
    world = []

    global Skrr
    Skrr = SKRR()
    world.append(Skrr)

    # 테스트용 몬스터 생성
    sword_knight = Knight_Sword(900, get_canvas_height() // 2)
    sword_knight.target = Skrr
    world.append(sword_knight)

    bow_knight = Knight_Bow(1100, get_canvas_height() // 2)
    bow_knight.target = Skrr
    world.append(bow_knight)

    tackle_knight = Knight_Tackle(700, get_canvas_height() // 2)
    tackle_knight.target = Skrr
    world.append(tackle_knight)

def update_world():
    for obj in world:
        obj.update()

def render_world():
    clear_canvas()
    for obj in world:
        obj.draw()
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