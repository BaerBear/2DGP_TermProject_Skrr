from pico2d import *
from SKRR import *
from Events import *

def reset_world():
    global world
    world = []

    global Skrr
    Skrr = SKRR()

    world.append(Skrr)

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
    handle_events(running, Skrr)
    update_world()
    render_world()
    delay(0.01)

close_canvas()