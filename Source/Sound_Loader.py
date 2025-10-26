import os
from pico2d import load_wav, load_music

class BGM_Loader:
    bgms = None

    def load_bgms(cls):
        if cls.bgms is not None:
            return cls.bgms

        cls.bgms = {}
        base_path = os.path.join(os.path.dirname(__file__), r'..\Resources\audio\Bgm')

        cls.bgms['chapter1'] = load_music(os.path.join(base_path, 'Chapter1.wav'))
        cls.bgms['chapter1_boss'] = load_music(os.path.join(base_path, 'Chapter1_Boss.wav'))
        cls.bgms['main_title'] = load_music(os.path.join(base_path, 'MainTitle_Hardmode.wav'))

        # 볼륨 조절
        for bgm in cls.bgms.values():
            bgm.set_volume(64)

        return cls.bgms

class SKRR_Sound_Loader:
    sounds = None

    def load_sounds(cls):
        if cls.sounds is not None:
            return cls.sounds

        cls.sounds = {}
        base_path = os.path.join(os.path.dirname(__file__), r'..\Resources\audio\Skul')

        # 플레이어 효과음 로드
        cls.sounds['jump'] = load_wav(os.path.join(base_path, 'Default_Jump.wav'))
        cls.sounds['jump_air'] = load_wav(os.path.join(base_path, 'Default_Jump_Air.wav'))
        cls.sounds['dash'] = load_wav(os.path.join(base_path, 'Default_Dash.wav'))
        cls.sounds['attack1'] = load_wav(os.path.join(base_path, 'Skul_Atk 1.wav'))
        cls.sounds['attack2'] = load_wav(os.path.join(base_path, 'Skul_Atk 2.wav'))
        cls.sounds['jump_attack'] = load_wav(os.path.join(base_path, 'Skul_Jump_Atk.wav'))
        cls.sounds['dead'] = load_wav(os.path.join(base_path, 'Default_Dead.wav'))

        for sound in cls.sounds.values():
            sound.set_volume(50)

        return cls.sounds

class Enemy_Sound_Loader:
    sounds = None

    def load_sounds(cls):
        if cls.sounds is not None:
            return cls.sounds

        cls.sounds = {}
        base_path = os.path.join(os.path.dirname(__file__), r'..\Resources\audio\Enemy')

        for sound in cls.sounds.values():
            sound.set_volume(50)

        return cls.sounds

class Object_Sound_Loader:
    sounds = None

    def load_sounds(cls):
        if cls.sounds is not None:
            return cls.sounds

        cls.sounds = {}
        base_path = os.path.join(os.path.dirname(__file__), r'..\Resources\audio\Object')

        for sound in cls.sounds.values():
            sound.set_volume(50)

        return cls.sounds

class UI_Sound_Loader:
    sounds = None

    def load_sounds(cls):
        if cls.sounds is not None:
            return cls.sounds

        cls.sounds = {}
        base_path = os.path.join(os.path.dirname(__file__), r'..\Resources\audio\UI')

        for sound in cls.sounds.values():
            sound.set_volume(50)

        return cls.sounds

class SoundManager:
    _initialized = False
    player_sounds = None
    enemy_sounds = None
    object_sounds = None
    ui_sounds = None
    bgms = None
    current_bgm = None

    def initialize(cls):
        if cls._initialized:
            return

        cls.player_sounds = SKRR_Sound_Loader.load_sounds()
        cls.enemy_sounds = Enemy_Sound_Loader.load_sounds()
        cls.object_sounds = Object_Sound_Loader.load_sounds()
        cls.ui_sounds = UI_Sound_Loader.load_sounds()
        cls.bgms = BGM_Loader.load_bgms()
        cls._initialized = True

    def play_player_sound(cls, sound_name):
        if cls.player_sounds and sound_name in cls.player_sounds:
            cls.player_sounds[sound_name].play()

    def play_enemy_sound(cls, sound_name):
        if cls.enemy_sounds and sound_name in cls.enemy_sounds:
            cls.enemy_sounds[sound_name].play()

    def play_object_sound(cls, sound_name):
        if cls.object_sounds and sound_name in cls.object_sounds:
            cls.object_sounds[sound_name].play()

    def play_ui_sound(cls, sound_name):
        if cls.ui_sounds and sound_name in cls.ui_sounds:
            cls.ui_sounds[sound_name].play()

    def play_bgm(cls, bgm_name, repeat=True):
        if cls.bgms and bgm_name in cls.bgms:
            if cls.current_bgm:
                cls.current_bgm.stop()

            cls.current_bgm = cls.bgms[bgm_name]
            if repeat:
                cls.current_bgm.repeat_play()
            else:
                cls.current_bgm.play()

    def stop_bgm(cls):
        if cls.current_bgm:
            cls.current_bgm.stop()
            cls.current_bgm = None

