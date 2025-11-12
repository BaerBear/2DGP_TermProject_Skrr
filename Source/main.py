from pico2d import *
import logo_mode as start_mode
import game_framework

open_canvas(game_framework.width, game_framework.height)
game_framework.run(start_mode)
close_canvas()