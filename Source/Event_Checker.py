from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDLK_RIGHT, SDLK_LEFT, SDLK_c, SDLK_x, SDLK_z, SDLK_a, SDLK_s, SDLK_d

# 이벤트 체크 함수들

def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT

def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT

def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT

def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT

def attack_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_c

def jump_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_x

def dash_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_z

def skill1_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a

def skill2_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_s

def skill3_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_d

def time_out(e):
    return e[0] == 'TIME_OUT'

def animation_end(e):
    return e[0] == 'ANIMATION_END'

def land_on_ground(e):
    return e[0] == 'LAND_ON_GROUND'

def start_falling(e):
    return e[0] == 'START_FALLING'

def combo_available(e):
    return e[0] == 'COMBO_AVAILABLE'

def dash_complete(e):
    return e[0] == 'DASH_COMPLETE'

def stop_moving(e):
    return e[0] == 'STOP_MOVING'

def dead(e):
    return e[0] == 'DEAD'

def respawn(e):
    return e[0] == 'RESPAWN'
