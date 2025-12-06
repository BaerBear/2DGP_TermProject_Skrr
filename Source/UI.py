from ResourceManager import ResourceManager

class UI:
    initialized = False
    cursor_image = None
    f_key_image = None
    player_info_image = None

    def __init__(self):
        if not UI.initialized:
            UI.cursor_image = ResourceManager.get_ui_images('cursor')
            UI.f_key_image = ResourceManager.get_ui_images('f_key')
            UI.player_info_image = ResourceManager.get_ui_images('player_info')
            UI.title_image = ResourceManager.get_ui_images('title')


            UI.initialized = True

    def draw_cursor(self, x, y):
        if UI.cursor_image:
            UI.cursor_image[0].clip_draw(0, 0, UI.cursor_image[0].w, UI.cursor_image[0].h,
                                         x + UI.cursor_image[0].w / 2, y - UI.cursor_image[0].h / 2)

    def draw_f_key(self, x, y):
        if UI.f_key_image:
            UI.f_key_image[0].clip_draw(0, 0, UI.f_key_image[0].w, UI.f_key_image[0].h, x, y)

    def draw_player_info(self, x, y):
        if UI.player_info_image:
            UI.player_info_image[0].clip_draw(0, 0, UI.player_info_image[0].w, UI.player_info_image[0].h, x * 2.5, y * 2.5,
                                              UI.player_info_image[0].w * 2.5, UI.player_info_image[0].h * 2.5)
