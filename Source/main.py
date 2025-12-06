from pico2d import *
from Sound_Loader import SoundManager
import play_mode as start_mode
import game_framework

open_canvas(game_framework.width, game_framework.height)
SoundManager.initialize()
game_framework.run(start_mode)
close_canvas()