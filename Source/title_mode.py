from pico2d import *
import game_framework
import play_mode

image = None

def init():
    global image
    image = load_image('../Resources/Image/Title_Logo.png')

def update():
    pass

def draw():
    clear_canvas()
    image.draw(1440 // 2, 900 // 2)
    update_canvas()

def finish():
    global image
    del image

def handle_events():
    events = get_events()
    for e in events:
        if e.type == SDL_KEYDOWN and e.key == SDLK_SPACE:
            game_framework.change_mode(play_mode)
        elif e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN and e.key == SDLK_ESCAPE:
            game_framework.quit()

def pause():
    pass

def resume():
    pass

