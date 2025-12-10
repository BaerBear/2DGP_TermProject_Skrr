from Enemy import Knight_Sword, Knight_Bow, Knight_Tackle
from Boss import GrimReaper
import game_world

class StageManager:
    """스테이지별 적 배치 정보를 관리하는 클래스"""

    ENEMY_Y_OFFSETS = {
        Knight_Sword: 0,
        Knight_Bow: 1,
        Knight_Tackle: -3,
        GrimReaper: 0
    }

    # (적 클래스, x좌표, y좌표) - y좌표가 None이면 player_start_y 사용
    STAGE_ENEMIES = {
        0: [  # Stage0
            (Knight_Sword, 800, 256),
            (Knight_Bow, 1200, 256),
        ],
        1: [  # Stage1
            # First Wave - 시작 지점
            (Knight_Sword, 700, 608),
            (Knight_Bow, 600, 608),

            # Second Wave - 중간 지점
            (Knight_Tackle, 1700, 672),
            (Knight_Sword, 1500, 608),
            (Knight_Bow, 1600, 608),
            (Knight_Sword, 1800, 608),

            # Third Wave - 상단 플랫폼
            (Knight_Sword, 700, 1440),
            (Knight_Bow, 600, 1440),
            (Knight_Tackle, 1100, 1376),
            (Knight_Sword, 1400, 1312),
            (Knight_Bow, 1200, 1312),

        ],
        2: [  # BossStage
            (GrimReaper, 1400, 320),
        ]
    }

    @staticmethod
    def load_stage_enemies(stage_num, player, tile_map=None):
        import SKRR
        enemies = []

        if stage_num not in StageManager.STAGE_ENEMIES:
            # print(f"Warning: Stage {stage_num} has no enemy configuration")
            return enemies

        player_start_x, player_start_y = SKRR.stage_start_positions.get(stage_num, (100, 600))

        enemy_configs = StageManager.STAGE_ENEMIES[stage_num]

        for config in enemy_configs:
            if len(config) == 2:
                enemy_class, x = config
                y = None
            else:
                enemy_class, x, y = config

            if y is None:
                y_offset = StageManager.ENEMY_Y_OFFSETS.get(enemy_class, 0)
                y = player_start_y + y_offset

            enemy = enemy_class(x, y)
            enemy.target = player

            if tile_map:
                enemy.set_tile_map(tile_map)

            game_world.add_object(enemy, 1)  # Layer 1에 추가

            # 플레이어 공격과 적의 충돌 쌍에 적 추가
            game_world.add_collision_pair('player_attack:enemy', None, enemy)

            enemies.append(enemy)
            # print(f"  - Spawned {enemy_class.__name__} at ({x}, {y})")

        # print(f"Stage {stage_num}: Loaded {len(enemies)} enemies")
        return enemies

    @staticmethod
    def clear_all_enemies():
        # Layer 1 모든 객체 제거
        objects_to_remove = game_world.world[1].copy() if len(game_world.world) > 1 else []
        for obj in objects_to_remove:
            game_world.remove_object(obj)
        # print("All enemies cleared")
