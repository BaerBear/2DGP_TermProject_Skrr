import os
from pico2d import load_wav, load_music


class SoundManager:
    _initialized = False
    player_sounds = None
    enemy_sounds = None
    object_sounds = None
    ui_sounds = None
    bgms = None
    current_bgm = None

    Effect_Volume = 7
    BGM_Volume = 8

    @classmethod
    def initialize(cls):
        if cls._initialized:
            return

        audio_path = os.path.join(os.path.dirname(__file__), r'..\Resources\audio')
        skul_path = os.path.join(audio_path, 'Skul')

        # 플레이어 사운드
        cls.player_sounds = {}
        cls.player_sounds['Jump'] = load_wav(os.path.join(skul_path, 'Default_Jump.wav'))
        cls.player_sounds['Jump_air'] = load_wav(os.path.join(skul_path, 'Default_Jump_Air.wav'))
        cls.player_sounds['Dash'] = load_wav(os.path.join(skul_path, 'Default_Dash.wav'))
        cls.player_sounds['Attack1'] = load_wav(os.path.join(skul_path, 'Skul_Atk_1.wav'))
        cls.player_sounds['Attack2'] = load_wav(os.path.join(skul_path, 'Skul_Atk_2.wav'))
        cls.player_sounds['Jump_attack'] = load_wav(os.path.join(skul_path, 'Skul_Jump_Atk.wav'))
        cls.player_sounds['Dead'] = load_wav(os.path.join(skul_path, 'Default_Dead.wav'))

        for sound in cls.player_sounds.values():
            sound.set_volume(cls.Effect_Volume)

        # 적 사운드
        Enemy_path = os.path.join(audio_path, 'Enemy')
        cls.enemy_sounds = {}
        cls.enemy_sounds['enemy_dead'] = load_wav(os.path.join(Enemy_path, 'Enemy_Dead.wav'))
        cls.enemy_sounds['enemy_big_dead'] = load_wav(os.path.join(Enemy_path, 'Enemy_Big_Dead.wav'))
        cls.enemy_sounds['arrow_ready'] = load_wav(os.path.join(Enemy_path, 'Crossbow_Ready.wav'))
        cls.enemy_sounds['arrow_fire'] = load_wav(os.path.join(Enemy_path, 'Crossbow_Fire.wav'))
        cls.enemy_sounds['blast_hit'] = load_wav(os.path.join(Enemy_path, 'Attack_Sword.wav'))

        for sound in cls.enemy_sounds.values():
            sound.set_volume(cls.Effect_Volume)

        # 오브젝트 사운드
        Object_path = os.path.join(audio_path, 'Object')
        cls.object_sounds = {}
        cls.object_sounds['gain_gold'] = load_wav(os.path.join(Object_path, 'Object_GainGold.wav'))
        cls.object_sounds['gain_item'] = load_wav(os.path.join(Object_path, 'Object_GainItem.wav'))
        cls.object_sounds['open_box'] = load_wav(os.path.join(Object_path, 'Object_OpenBox.wav'))

        for sound in cls.object_sounds.values():
            sound.set_volume(cls.Effect_Volume)

        # UI 사운드
        UI_path = os.path.join(audio_path, 'UI')
        cls.ui_sounds = {}
        cls.ui_sounds['open'] = load_wav(os.path.join(UI_path, 'UI_Open.wav'))
        cls.ui_sounds['close'] = load_wav(os.path.join(UI_path, 'UI_Close.wav'))
        cls.ui_sounds['move'] = load_wav(os.path.join(UI_path, 'UI_Move.wav'))
        cls.ui_sounds['talk'] = load_wav(os.path.join(UI_path, 'UI_Talk.wav'))
        cls.ui_sounds['inventory_open'] = load_wav(os.path.join(UI_path, 'UI_Inventory_Open.wav'))
        cls.ui_sounds['inventory_close'] = load_wav(os.path.join(UI_path, 'UI_Inventory_Close.wav'))
        cls.ui_sounds['get_ability'] = load_wav(os.path.join(UI_path, 'UI_GetAbility.wav'))
        cls.ui_sounds['mythology_unlock'] = load_wav(os.path.join(UI_path, 'UI_MythologyUnlock.wav'))

        for sound in cls.ui_sounds.values():
            sound.set_volume(cls.Effect_Volume)

        # 배경 음악
        Bgm_path = os.path.join(audio_path, 'Bgm')
        cls.bgms = {}
        cls.bgms['chapter1'] = load_music(os.path.join(Bgm_path, 'Chapter1.wav'))
        cls.bgms['chapter1_boss'] = load_music(os.path.join(Bgm_path, 'Chapter1_Boss.wav'))
        cls.bgms['main_title'] = load_music(os.path.join(Bgm_path, 'MainTitle_Hardmode.wav'))

        for bgm in cls.bgms.values():
            bgm.set_volume(cls.BGM_Volume)

        cls._initialized = True

    @classmethod
    def play_player_sound(cls, sound_name):
        if cls.player_sounds and sound_name in cls.player_sounds:
            cls.player_sounds[sound_name].play()

    @classmethod
    def play_enemy_sound(cls, sound_name):
        if cls.enemy_sounds and sound_name in cls.enemy_sounds:
            cls.enemy_sounds[sound_name].play()

    @classmethod
    def play_object_sound(cls, sound_name):
        if cls.object_sounds and sound_name in cls.object_sounds:
            cls.object_sounds[sound_name].play()

    @classmethod
    def play_ui_sound(cls, sound_name):
        if cls.ui_sounds and sound_name in cls.ui_sounds:
            cls.ui_sounds[sound_name].play()

    @classmethod
    def play_bgm(cls, bgm_name, repeat=True):
        if cls.bgms and bgm_name in cls.bgms:
            if cls.current_bgm:
                cls.current_bgm.stop()

            cls.current_bgm = cls.bgms[bgm_name]
            if repeat:
                cls.current_bgm.repeat_play()
            else:
                cls.current_bgm.play()

    @classmethod
    def stop_bgm(cls):
        if cls.current_bgm:
            cls.current_bgm.stop()
            cls.current_bgm = None
