from pico2d import *
import game_framework
import title_mode
import common

image = None
logo_start_time = 0.0

def init():
    global image, logo_start_time
    image = load_image('../Resources/Image/Skrr_Ai_image_fill.png')
    logo_start_time = get_time()

    # 모든 싱글톤 리소스 미리 로딩
    common.initialize()

def update():
    if get_time() - logo_start_time > 2.0:
        game_framework.change_mode(title_mode)

def draw():
    clear_canvas()
    hide_cursor()
    image.draw(game_framework.width // 2, game_framework.height // 2)
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
        elif e.type == SDL_MOUSEBUTTONDOWN and e.button == SDL_BUTTON_LEFT:
            print(f"Mouse Left Click: ({e.x}, {get_canvas_height() - e.y})")

def pause():
    pass

def resume():
    pass
