from pico2d import *
import game_framework
import title_mode

image = None
logo_start_time = 0.0

def init():
    global image, logo_start_time
    image = load_image('../Resources/Image/Skrr_Ai_image_fill.png')
    logo_start_time = get_time()

def update():
    if get_time() - logo_start_time > 2.0:
        game_framework.change_mode(title_mode)

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
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN and e.key == SDLK_ESCAPE:
            game_framework.quit()

def pause():
    pass

def resume():
    pass

