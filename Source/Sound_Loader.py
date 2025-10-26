import os
from pico2d import load_wav, load_music


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

