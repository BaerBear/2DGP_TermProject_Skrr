from pico2d import *

from ResourceManager import ResourceManager
import game_framework


class UI:
    initialized = False
    cursor_image = None
    f_key_image = None
    player_info_image = None
    player_hp_bar_image = None
    gold_image = None
    boss_hp_bar_image = None
    boss_hp_info_image = None
    boss_name_info_image = None
    font = None

    def __init__(self):
        if not UI.initialized:
            UI.cursor_image = ResourceManager.get_ui_images('cursor')
            UI.f_key_image = ResourceManager.get_ui_images('f_key')
            UI.player_info_image = ResourceManager.get_ui_images('player_info')
            UI.player_hp_bar_image = ResourceManager.get_ui_images('player_hp_bar')
            UI.gold_image = ResourceManager.get_ui_images('gold_icon')
            UI.font = load_font(r'..\Resources\font\Perfect_DOS_VGA_437.ttf', 24)
            UI.boss_hp_bar_image = ResourceManager.get_ui_images('boss_hp_bar')
            UI.boss_hp_info_image = ResourceManager.get_ui_images('boss_hp_info')
            UI.boss_name_info_image = ResourceManager.get_ui_images('boss_name_info')
            UI.initialized = True

    def draw_cursor(self, x, y):
        if UI.cursor_image:
            UI.cursor_image[0].clip_draw(0, 0, UI.cursor_image[0].w, UI.cursor_image[0].h,
                                         x + UI.cursor_image[0].w / 2, y - UI.cursor_image[0].h / 2)

    def draw_f_key(self, x, y):
        if UI.f_key_image:
            UI.f_key_image[0].clip_draw(0, 0, UI.f_key_image[0].w, UI.f_key_image[0].h, x, y
                                        , UI.f_key_image[0].w * 1.5, UI.f_key_image[0].h * 1.5)

    def draw_player_info(self, x, y, current_hp, max_hp):
        percent = current_hp / max_hp
        if UI.player_info_image:
            UI.player_info_image[0].clip_draw(0, 0, UI.player_info_image[0].w, UI.player_info_image[0].h, x * 2.5, y * 2.5,
                                              UI.player_info_image[0].w * 2.5, UI.player_info_image[0].h * 2.5)

            if percent > 0:
                bar_width = UI.player_hp_bar_image[0].w * 2.5
                current_width = bar_width * percent
                offset_x = (bar_width - current_width) / 2  # 줄어든 너비의 절반

                UI.player_hp_bar_image[0].clip_draw(
                    0, 0,
                    UI.player_hp_bar_image[0].w, UI.player_hp_bar_image[0].h,
                    x * 2.5 + 46 - offset_x,
                    y * 2.5 - 39.5,
                    current_width,
                    UI.player_hp_bar_image[0].h * 2.5
                )

            if UI.font:
                hp_text = f'{current_hp}' + '/' + f'{max_hp}'
                if current_hp >= 100:
                    offset = 0
                elif current_hp >= 10:
                    offset = 14
                else:
                    offset = 28
                UI.font.draw(x * 2.5 + offset, y * 2.5 - 39.5, hp_text, (255, 255, 255))

    def draw_gold_icon(self, x, y, gold_amount):
        if UI.gold_image:
            UI.gold_image[0].clip_draw(0, 0, UI.gold_image[0].w, UI.gold_image[0].h, x, y,
                                       UI.gold_image[0].w * 2.5, UI.gold_image[0].h* 2.5)

            if UI.font:
                gold_text = f'{gold_amount}'
                UI.font.draw(x + (UI.gold_image[0].w / 2) + 14, y, gold_text, (255, 255, 255))

    def draw_boss_hp(self, current_hp, max_hp):
        percent = current_hp / max_hp
        if UI.boss_hp_bar_image:
            x = game_framework.width / 2
            y = game_framework.height - 20
            if percent > 0:
                bar_width = UI.boss_hp_bar_image[0].w * 10
                current_width = bar_width * percent
                offset_x = (bar_width - current_width) / 2

                UI.boss_name_info_image[0].clip_draw(0,0 , UI.boss_name_info_image[0].w, UI.boss_name_info_image[0].h,
                                                     x, y, UI.boss_name_info_image[0].w * 2, UI.boss_name_info_image[0].h * 2.0)

                UI.boss_hp_info_image[0].clip_draw(0,0, UI.boss_hp_info_image[0].w, UI.boss_hp_info_image[0].h,
                                                  x, y - 30, bar_width, UI.boss_hp_info_image[0].h * 2)

                UI.boss_hp_bar_image[0].clip_draw(0, 0, UI.boss_hp_bar_image[0].w, UI.boss_hp_bar_image[0].h,
                    x - offset_x, y - 30, current_width, UI.boss_hp_bar_image[0].h * 2)

            if UI.font:
                hp_text = f'{current_hp}' + '/' + f'{max_hp}'
                name_text = f'{"Grim Reaper"}'
                if current_hp >= 1000:
                    offset = 0
                elif current_hp >= 100:
                    offset = 14
                elif current_hp >= 10:
                    offset = 28
                else:
                    offset = 42
                UI.font.draw(x + offset - 60, y - 30, hp_text, (255, 255, 255))
                UI.font.draw(x - 75, y + 1, name_text, (255, 255, 255))