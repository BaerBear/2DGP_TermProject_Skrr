from pico2d import *


def handle_events(running, skrr):
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        elif event.type == SDL_KEYDOWN:
            running = handle_key_down(event, skrr)
        elif event.type == SDL_KEYUP:
            handle_key_up(event, skrr)
    return running


def handle_key_down(event, skrr):
    if event.key == SDLK_RIGHT:
        handle_right_down(skrr, event)
    elif event.key == SDLK_LEFT:
        handle_left_down(skrr, event)
    elif event.key == SDLK_c:
        handle_attack(skrr, event)
    elif event.key == SDLK_x:
        handle_jump(skrr, event)
    elif event.key == SDLK_z:
        handle_dash(skrr, event)
    elif event.key == SDLK_a:
        handle_a_down(skrr, event)
    elif event.key == SDLK_s:
        handle_s_down(skrr, event)
    elif event.key == SDLK_d:
        handle_d_down(skrr, event)
    return True


def handle_right_down(skrr, event):
    skrr.key_pressed['right'] = True
    if skrr.state_machine.current_state != skrr.DASH:
        skrr.face_dir = 1
    skrr.is_moving = True
    skrr.handle_event(('INPUT', event))


def handle_left_down(skrr, event):
    skrr.key_pressed['left'] = True
    if skrr.state_machine.current_state != skrr.DASH:
        skrr.face_dir = -1
    skrr.is_moving = True
    skrr.handle_event(('INPUT', event))


def handle_attack(skrr, event):
    if skrr.attack_type == 'B':
        return

    if skrr.state_machine.current_state == skrr.ATTACK and skrr.attack_type == 'A' and 18 <= skrr.frame < 30:
        skrr.attack_type = 'B'
        skrr.state_machine.handle_event(('COMBO_AVAILABLE', None))
    elif skrr.jumping and skrr.is_jumpattack_ready():
        skrr.handle_event(('INPUT', event))
    elif not skrr.jumping:
        if skrr.attack_type is None:
            skrr.attack_type = 'A'
            skrr.handle_event(('INPUT', event))


def handle_jump(skrr, event):
    if skrr.state_machine.current_state == skrr.ATTACK or skrr.state_machine.current_state == skrr.JUMPATTACK:
        return

    if skrr.is_grounded and skrr.jump_count == 0:
        skrr.handle_event(('INPUT', event))
    elif not skrr.is_grounded and skrr.jump_count == 1:
        skrr.handle_event(('INPUT', event))


def handle_dash(skrr, event):
    if not skrr.is_dash_ready():
        return
    if skrr.state_machine.current_state == skrr.ATTACK or skrr.state_machine.current_state == skrr.JUMPATTACK:
        return

    if skrr.dash_type is None:
        skrr.dash_type = 0
        skrr.handle_event(('INPUT', event))
    elif skrr.dash_type == 0 and skrr.state_machine.current_state == skrr.DASH and skrr.DASH.can_second_dash:
        skrr.dash_type = 1
        skrr.handle_event(('INPUT', event))


def handle_key_up(event, skrr):
    if event.key == SDLK_RIGHT:
        handle_right_up(skrr)
    elif event.key == SDLK_LEFT:
        handle_left_up(skrr)


def handle_right_up(skrr):
    skrr.key_pressed['right'] = False
    if skrr.key_pressed['left']:
        skrr.face_dir = -1
        skrr.is_moving = True
    else:
        skrr.is_moving = False
        skrr.state_machine.handle_event(('STOP_MOVING', None))


def handle_left_up(skrr):
    skrr.key_pressed['left'] = False
    if skrr.key_pressed['right']:
        skrr.face_dir = 1
        skrr.is_moving = True
    else:
        skrr.is_moving = False
        skrr.state_machine.handle_event(('STOP_MOVING', None))

def handle_a_down(skrr, event):
    skrr.state_machine.handle_event(('INPUT', event))

def handle_s_down(skrr, event):
    skrr.state_machine.handle_event(('INPUT', event))

def handle_d_down(skrr, event):
    skrr.state_machine.handle_event(('INPUT', event))