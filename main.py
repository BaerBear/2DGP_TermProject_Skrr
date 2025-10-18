from pico2d import *







open_canvas(1440, 900)
reset_world()

# game loop
while running:
    handle_events()
    update_world()
    render_world()
    delay(0.01)

close_canvas()