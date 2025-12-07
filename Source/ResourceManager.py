"""
ResourceManager - 중앙 리소스 관리 시스템
모든 이미지와 사운드를 한 곳에서 관리하여 중복 로딩 방지 및 메모리 최적화
"""

import Image_Loader
from pico2d import load_image
import os


class ResourceManager:
    _instance = None
    _initialized = False

    # 캐시 딕셔너리
    _image_cache = {}
    _player_images = None
    _enemy_images = {}
    _boss_images = {}
    _effect_images = None
    _object_images = None
    _ui_images = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def initialize(cls):
        if cls._initialized:
            return

        print("리소스 로딩 시작")

        # 플레이어 이미지 로드
        cls._load_player_images()

        # 적 이미지 로드
        cls._load_enemy_images()

        # 보스 이미지 로드
        cls._load_boss_images()

        # 공통 이펙트 이미지 로드
        cls._load_effect_images()

        cls._load_object_images()

        # UI 이미지 로드
        cls._load_ui_images()

        cls._initialized = True
        print("리소스 로딩 완료")

    @classmethod
    def _load_player_images(cls):
        if cls._player_images is not None:
            return

        print("  - 플레이어 이미지 로딩...")
        cls._player_images = {
            'Idle': Image_Loader.SKRR_Image_Loader('Idle').images,
            'Wait': Image_Loader.SKRR_Image_Loader('Wait').images,
            'Walk': Image_Loader.SKRR_Image_Loader('Walk').images,
            'AttackA': Image_Loader.SKRR_Image_Loader('AttackA').images,
            'AttackB': Image_Loader.SKRR_Image_Loader('AttackB').images,
            'Jump': Image_Loader.SKRR_Image_Loader('Jump').images,
            'JumpEffect': Image_Loader.SKRR_Image_Loader('JumpEffect').images,
            'JumpAttack': Image_Loader.SKRR_Image_Loader('JumpAttack').images,
            'Reborn': Image_Loader.SKRR_Image_Loader('Reborn').images,
            'Dash': Image_Loader.SKRR_Image_Loader('Dash').images,
            'DashEffect': Image_Loader.SKRR_Image_Loader('DashEffect').images,
            'Fall': Image_Loader.SKRR_Image_Loader('Fall').images,
            'Dead': Image_Loader.SKRR_Image_Loader('Dead').images,
            'Touch': Image_Loader.SKRR_Image_Loader('Touch').images,
            'Skill1': Image_Loader.SKRR_Image_Loader('Skill1').images,
            'Skill2': Image_Loader.SKRR_Image_Loader('Skill2').images,
            'Skill2_Start': Image_Loader.SKRR_Image_Loader('Skill2_Start').images,
            'Skill2_Effect': Image_Loader.SKRR_Image_Loader('Skill2_Effect').images,
            'Skill3_ground': Image_Loader.SKRR_Image_Loader('Skill3_ground').images,
            'Skill3_air': Image_Loader.SKRR_Image_Loader('Skill3_air').images,
        }

    @classmethod
    def _load_enemy_images(cls):
        print("  - 적 이미지 로딩...")

        # Knight_Sword
        if 'Knight_Sword' not in cls._enemy_images:
            cls._enemy_images['Knight_Sword'] = {
                'walk': Image_Loader.Enemy_Image_Loader('Knight_Sword', 'Walk').images,
                'attack': Image_Loader.Enemy_Image_Loader('Knight_Sword', 'Attack').images,
                'hit': Image_Loader.Enemy_Image_Loader('Knight_Sword', 'Hit').images,
                'idle': Image_Loader.Enemy_Image_Loader('Knight_Sword', 'Idle').images,
            }

        # Knight_Bow
        if 'Knight_Bow' not in cls._enemy_images:
            cls._enemy_images['Knight_Bow'] = {
                'walk': Image_Loader.Enemy_Image_Loader('Knight_Bow', 'Walk').images,
                'attack': Image_Loader.Enemy_Image_Loader('Knight_Bow', 'Attack').images,
                'hit': Image_Loader.Enemy_Image_Loader('Knight_Bow', 'Hit').images,
                'idle': Image_Loader.Enemy_Image_Loader('Knight_Bow', 'Idle').images,
                'attack_sign': Image_Loader.Enemy_Image_Loader('Knight_Bow', 'Attack_Sign').images,
            }

        # Knight_Tackle
        if 'Knight_Tackle' not in cls._enemy_images:
            cls._enemy_images['Knight_Tackle'] = {
                'walk': Image_Loader.Enemy_Image_Loader('Knight_Tackle', 'Walk').images,
                'attack': Image_Loader.Enemy_Image_Loader('Knight_Tackle', 'Attack').images,
                'tackle': Image_Loader.Enemy_Image_Loader('Knight_Tackle', 'Tackle').images,
                'tackle_effect': Image_Loader.Enemy_Image_Loader('Knight_Tackle', 'Tackle_Effect').images,
                'idle': Image_Loader.Enemy_Image_Loader('Knight_Tackle', 'Idle').images,
            }

    @classmethod
    def _load_boss_images(cls):
        print("  - 보스 이미지 로딩...")

        # GrimReaper
        if 'GrimReaper' not in cls._boss_images:
            cls._boss_images['GrimReaper'] = {
                'idle': Image_Loader.Boss_Image_Loader('GrimReaper', 'Idle').images,
                'walk': Image_Loader.Boss_Image_Loader('GrimReaper', 'Walk').images,
                'attack': Image_Loader.Boss_Image_Loader('GrimReaper', 'Attack').images,
                'skill1_effect': Image_Loader.Boss_Image_Loader('GrimReaper', 'Skill1_Effect').images,
                'skill1_motion': Image_Loader.Boss_Image_Loader('GrimReaper', 'Skill1_Motion').images,
                'skill2_fire': Image_Loader.Boss_Image_Loader('GrimReaper', 'Skill2_Fire').images,
                'skill2_motion': Image_Loader.Boss_Image_Loader('GrimReaper', 'Skill2_Motion').images,
            }

    @classmethod
    def _load_effect_images(cls):
        if cls._effect_images is not None:
            return
        print("  - 이펙트 이미지 로딩...")

        cls._effect_images = {
            'enemy_dead': Image_Loader.Effect_Image_Loader('Enemy_Dead').images,
        }

    @classmethod
    def _load_object_images(cls):
        if cls._object_images is not None:
            return
        print("  - 오브젝트 이미지 로딩...")

        cls._object_images = {
            'coin': Image_Loader.Object_Image_Loader('Coin').images,
            'chest': Image_Loader.Object_Image_Loader('Chest').images,
            'gate_open': Image_Loader.Object_Image_Loader('Gate_Open').images,
            'gate_close': Image_Loader.Object_Image_Loader('Gate_Close').images,
        }

    @classmethod
    def _load_ui_images(cls):
        if cls._ui_images is not None:
            return
        print("  - UI 이미지 로딩...")

        cls._ui_images = {
            'player_info': Image_Loader.UI_Image_Loader('Player_Info').images,
            'cursor': Image_Loader.UI_Image_Loader('Cursor').images,
            'f_key': Image_Loader.UI_Image_Loader('F_key').images,
            'player_hp_bar': Image_Loader.UI_Image_Loader('Player_HP_Bar').images,
            'gold_icon': Image_Loader.UI_Image_Loader('Gold_Icon').images,
        }

    @classmethod
    def get_player_images(cls):
        if not cls._initialized:
            cls.initialize()
        return cls._player_images

    @classmethod
    def get_enemy_images(cls, enemy_type):
        if not cls._initialized:
            cls.initialize()
        return cls._enemy_images.get(enemy_type, {})

    @classmethod
    def get_boss_images(cls, boss_type):
        """보스 이미지 가져오기"""
        if not cls._initialized:
            cls.initialize()
        return cls._boss_images.get(boss_type, {})

    @classmethod
    def get_effect_images(cls, effect_name):
        if not cls._initialized:
            cls.initialize()
        return cls._effect_images.get(effect_name, [])

    @classmethod
    def get_object_images(cls, object_name):
        if not cls._initialized:
            cls.initialize()
        return cls._object_images.get(object_name, [])

    @classmethod
    def get_ui_images(cls, ui_element):
        if not cls._initialized:
            cls.initialize()
        return cls._ui_images.get(ui_element, [])

    @classmethod
    def preload_resources(cls):
        cls.initialize()

    @classmethod
    def clear_cache(cls):
        print("캐시 클리어")
        cls._image_cache.clear()

    @classmethod
    def unload_all(cls):
        print("모든 리소스 언로드")
        cls._image_cache.clear()
        cls._player_images = None
        cls._enemy_images.clear()
        cls._boss_images.clear()
        cls._effect_images.clear()
        cls._initialized = False


# 싱글톤 인스턴스
resource_manager = ResourceManager()
