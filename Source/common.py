"""
게임 전역에서 사용되는 싱글톤 클래스들을 관리하는 모듈
게임 시작 시 한 번만 초기화되고 모든 모드에서 공유됨
"""

from ResourceManager import ResourceManager
from Sound_Loader import SoundManager
from Camera import Camera

# 싱글톤 인스턴스들
_initialized = False
_resource_manager = None
_sound_manager = None
_camera = None


def initialize():
    """모든 싱글톤 매니저를 초기화 (게임 시작 시 한 번만 호출)"""
    global _initialized, _resource_manager, _sound_manager, _camera

    if _initialized:
        print("Common 모듈은 이미 초기화되었습니다.")
        return

    print("=== Common 모듈 초기화 시작 ===")

    # ResourceManager 초기화
    print("리소스 매니저 초기화...")
    _resource_manager = ResourceManager
    _resource_manager.preload_resources()

    # SoundManager 초기화
    print("사운드 매니저 초기화...")
    _sound_manager = SoundManager

    # Camera 초기화
    print("카메라 초기화...")
    _camera = Camera.get_instance()

    _initialized = True
    print("=== Common 모듈 초기화 완료 ===\n")


def get_resource_manager():
    """ResourceManager 인스턴스 반환"""
    if not _initialized:
        initialize()
    return _resource_manager


def get_sound_manager():
    """SoundManager 인스턴스 반환"""
    if not _initialized:
        initialize()
    return _sound_manager


def get_camera():
    """Camera 인스턴스 반환"""
    if not _initialized:
        initialize()
    return _camera


def is_initialized():
    """초기화 여부 반환"""
    return _initialized


def cleanup():
    """모든 매니저 정리 (게임 종료 시 호출)"""
    global _initialized, _resource_manager, _sound_manager, _camera

    if not _initialized:
        return

    print("=== Common 모듈 정리 시작 ===")

    # SoundManager 정리
    if _sound_manager:
        _sound_manager.stop_bgm()

    _resource_manager = None
    _sound_manager = None
    _camera = None
    _initialized = False

    print("=== Common 모듈 정리 완료 ===")

