from pico2d import *
import common
import game_framework

image = None
mx, my = 0, 0

def init():
    global image
    image = []
    image.append(load_image(os.path.join(os.path.dirname(os.path.abspath(__file__)), r'Resources', 'Image', 'UI', 'Ending_Title.png')))

    sound_manager = common.get_sound_manager()
    sound_manager.stop_bgm()
    sound_manager.play_bgm('main_title', repeat=True)

def update():
    pass

def draw():
    clear_canvas()
    hide_cursor()
    ui = common.get_ui()
    image[0].draw(game_framework.width // 2, game_framework.height // 2)
    ui.draw_press_space(game_framework.width // 2 - 230, 100)
    ui.draw_cursor(mx, my)
    update_canvas()

def finish():
    pass

def handle_events():
    events = get_events()
    for e in events:
        if e.type == SDL_KEYDOWN and e.key == SDLK_SPACE:
            import title_mode
            game_framework.change_mode(title_mode)
        elif e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN and e.key == SDLK_ESCAPE:
            game_framework.quit()
        elif e.type == SDL_MOUSEMOTION:
            global mx, my
            mx, my = e.x, get_canvas_height() - e.y

def pause():
    pass

def resume():
    pass

