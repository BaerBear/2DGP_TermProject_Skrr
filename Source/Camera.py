from pico2d import *
import game_framework

class Camera:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Camera()
        return cls._instance

    def __init__(self):
        self.x = 0
        self.y = 0
        self.target = None

        # 카메라 범위 제한 (맵 크기에 맞게 조정 가능)
        self.min_x = 0
        self.max_x = 10000  # 맵의 최대 너비
        self.min_y = 0
        self.max_y = 10000  # 맵의 최대 높이

        # 카메라 부드러운 이동을 위한 값
        self.smoothness = 0.1  # 0에 가까울수록 더 부드럽게

    def set_target(self, target):
        """카메라가 따라갈 타겟 설정 (주로 플레이어)"""
        self.target = target

    def set_bounds(self, min_x, max_x, min_y, max_y):
        """카메라 이동 범위 설정"""
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    def update(self):
        """카메라 위치 업데이트"""
        if self.target:
            # 타겟을 화면 중앙에 배치
            target_x = self.target.x - game_framework.width // 2
            target_y = self.target.y - game_framework.height // 2

            # 부드러운 카메라 이동 (선형 보간)
            self.x += (target_x - self.x) * self.smoothness
            self.y += (target_y - self.y) * self.smoothness

            # 카메라 범위 제한
            self.x = max(self.min_x, min(self.x, self.max_x - game_framework.width))
            self.y = max(self.min_y, min(self.y, self.max_y - game_framework.height))

    def apply(self, x, y):
        """월드 좌표를 화면 좌표로 변환"""
        return x - self.x, y - self.y

    def get_position(self):
        """카메라의 현재 위치 반환"""
        return self.x, self.y

