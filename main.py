from pico2d import *
from SKRR import *

def handle_events():
    global running
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False

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
    handle_events()
    update_world()
    render_world()
    delay(0.01)

close_canvas()