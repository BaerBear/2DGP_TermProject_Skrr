from pico2d import *
import common
import game_framework
import play_mode

image = None
mx, my = 0, 0

def init():
    global image
    image = []
    image.append(load_image('../Resources/Image/UI/Skrr_Ai_image_fill.png'))

    sound_manager = common.get_sound_manager()
    sound_manager.play_bgm('main_title', repeat=True)

def update():
    pass

def draw():
    clear_canvas()
    hide_cursor()
    ui = common.get_ui()
    image[0].draw(game_framework.width // 2, game_framework.height // 2)
    ui.draw_press_space(game_framework.width // 2 - 230, 70)
    ui.draw_cursor(mx, my)
    update_canvas()

def finish():
    pass

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
            pass
        elif e.type == SDL_MOUSEMOTION:
            global mx, my
            mx, my = e.x, get_canvas_height() - e.y

def pause():
    pass

def resume():
    pass
