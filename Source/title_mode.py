from pico2d import *
from Sound_Loader import SoundManager
import game_framework
import play_mode

image = None

def init():
    global image
    image = []
    image.append(load_image('../Resources/Image/Title_Art.png'))
    image.append(load_image('../Resources/Image/Title_Logo.png'))

    SoundManager.play_bgm('main_title', repeat=True)

def update():
    pass

def draw():
    clear_canvas()
    image[0].draw(game_framework.width // 2, game_framework.height // 2)
    image[1].draw(game_framework.width // 2, game_framework.height // 2)
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
        elif e.type == SDL_MOUSEBUTTONDOWN and e.button == SDL_BUTTON_LEFT:
            print(f"Mouse Left Click: ({e.x}, {get_canvas_height() - e.y})")

def pause():
    pass

def resume():
    pass
