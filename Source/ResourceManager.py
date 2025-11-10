"""
ResourceManager - 중앙 리소스 관리 시스템
모든 이미지와 사운드를 한 곳에서 관리하여 중복 로딩 방지 및 메모리 최적화
"""

from Image_Loader import SKRR_Image_Loader, Enemy_Image_Loader
from pico2d import load_image
import os


class ResourceManager:
    _instance = None
    _initialized = False

    # 캐시 딕셔너리
    _image_cache = {}
    _player_images = None
    _enemy_images = {}
    _effect_images = {}

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

        # 공통 이펙트 이미지 로드
        cls._load_effect_images()

        cls._initialized = True
        print("리소스 로딩 완료")

    @classmethod
    def _load_player_images(cls):
        if cls._player_images is not None:
            return

        print("  - 플레이어 이미지 로딩...")
        cls._player_images = {
            'Idle': SKRR_Image_Loader('Idle').images,
            'Wait': SKRR_Image_Loader('Wait').images,
            'Walk': SKRR_Image_Loader('Walk').images,
            'AttackA': SKRR_Image_Loader('AttackA').images,
            'AttackB': SKRR_Image_Loader('AttackB').images,
            'Jump': SKRR_Image_Loader('Jump').images,
            'JumpEffect': SKRR_Image_Loader('JumpEffect').images,
            'JumpAttack': SKRR_Image_Loader('JumpAttack').images,
            'Reborn': SKRR_Image_Loader('Reborn').images,
            'Dash': SKRR_Image_Loader('Dash').images,
            'DashEffect': SKRR_Image_Loader('DashEffect').images,
            'Fall': SKRR_Image_Loader('Fall').images,
            'Dead': SKRR_Image_Loader('Dead').images,
            'Touch': SKRR_Image_Loader('Touch').images,
            'Skill1': SKRR_Image_Loader('Skill1').images,
            'Skill2': SKRR_Image_Loader('Skill2').images,
            'Skill3_ground': SKRR_Image_Loader('Skill3_ground').images,
            'Skill3_air': SKRR_Image_Loader('Skill3_air').images,
        }

    @classmethod
    def _load_enemy_images(cls):
        print("  - 적 이미지 로딩...")

        # Knight_Sword
        if 'Knight_Sword' not in cls._enemy_images:
            cls._enemy_images['Knight_Sword'] = {
                'walk': Enemy_Image_Loader('Knight_Sword', 'Walk').images,
                'attack': Enemy_Image_Loader('Knight_Sword', 'Attack').images,
                'hit': Enemy_Image_Loader('Knight_Sword', 'Hit').images,
                'idle': Enemy_Image_Loader('Knight_Sword', 'Idle').images,
            }

        # Knight_Bow
        if 'Knight_Bow' not in cls._enemy_images:
            cls._enemy_images['Knight_Bow'] = {
                'walk': Enemy_Image_Loader('Knight_Bow', 'Walk').images,
                'attack': Enemy_Image_Loader('Knight_Bow', 'Attack').images,
                'hit': Enemy_Image_Loader('Knight_Bow', 'Hit').images,
                'idle': Enemy_Image_Loader('Knight_Bow', 'Idle').images,
            }

        # Knight_Tackle
        if 'Knight_Tackle' not in cls._enemy_images:
            cls._enemy_images['Knight_Tackle'] = {
                'walk': Enemy_Image_Loader('Knight_Tackle', 'Walk').images,
                'attack': Enemy_Image_Loader('Knight_Tackle', 'Attack').images,
                'tackle': Enemy_Image_Loader('Knight_Tackle', 'Tackle').images,
                'idle': Enemy_Image_Loader('Knight_Tackle', 'Idle').images,
            }

    @classmethod
    def _load_effect_images(cls):
        if 'enemy_dead' not in cls._effect_images:
            try:
                effect_path = os.path.join(os.path.dirname(__file__), r'..\Resources\Image\Effect\Enemy_Dead')
                cls._effect_images['enemy_dead'] = []
                for i in range(6):
                    img_path = os.path.join(effect_path, f'Enemy_Dead_{i}.png')
                    if os.path.exists(img_path):
                        cls._effect_images['enemy_dead'].append(load_image(img_path))
            except:
                print("적 죽음 이펙트 로드 실패")
                cls._effect_images['enemy_dead'] = []

        if 'hit_effect' not in cls._effect_images:
            try:
                effect_path = os.path.join(os.path.dirname(__file__), r'..\Resources\Image\Effect\Hit_Normal')
                cls._effect_images['hit_effect'] = []
                for i in range(12):
                    img_path = os.path.join(effect_path, f'Hit_Normal_{i}.png')
                    if os.path.exists(img_path):
                        cls._effect_images['hit_effect'].append(load_image(img_path))
            except:
                print("타격 이펙트 로드 실패")
                cls._effect_images['hit_effect'] = []

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
    def get_effect_images(cls, effect_name):
        if not cls._initialized:
            cls.initialize()
        return cls._effect_images.get(effect_name, [])

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
        cls._effect_images.clear()
        cls._initialized = False


# 싱글톤 인스턴스
resource_manager = ResourceManager()
