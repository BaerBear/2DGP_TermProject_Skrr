from Enemy import Knight_Sword, Knight_Bow, Knight_Tackle
import game_world

class StageManager:
    """스테이지별 적 배치 정보를 관리하는 클래스"""

    # 각 적 클래스별 y 오프셋 (플레이어 시작 위치 기준)
    # 각 적의 충돌 박스 크기 차이를 보정하기 위한 오프셋
    ENEMY_Y_OFFSETS = {
        Knight_Sword: 0,     # 기준 (height = 70)
        Knight_Bow: 3,       # 약간 작음 (height = 64) - 3픽셀 높게
        Knight_Tackle: -5    # 가장 큼 (height = 80) - 5픽셀 낮게
    }

    # (적 클래스, x좌표, y좌표)
    STAGE_ENEMIES = {
        0: [  # Stage0
            (Knight_Sword, 800),
            (Knight_Bow, 1200),
        ],
        1: [  # Stage1
            (Knight_Sword, 700),
            (Knight_Bow, 1100),
            (Knight_Tackle, 900),
            (Knight_Sword, 1500),
        ],
        2: [  # BossStage
            (Knight_Sword, 600),
            (Knight_Bow, 800),
            (Knight_Tackle, 1000),
            (Knight_Bow, 1200),
            (Knight_Sword, 1400),
        ]
    }

    @staticmethod
    def load_stage_enemies(stage_num, player, tile_map=None):
        import SKRR
        enemies = []

        if stage_num not in StageManager.STAGE_ENEMIES:
            print(f"Warning: Stage {stage_num} has no enemy configuration")
            return enemies

        player_start_x, player_start_y = SKRR.stage_start_positions.get(stage_num, (100, 600))

        enemy_configs = StageManager.STAGE_ENEMIES[stage_num]

        for enemy_class, x in enemy_configs:
            y_offset = StageManager.ENEMY_Y_OFFSETS.get(enemy_class, 0)
            y = player_start_y + y_offset

            enemy = enemy_class(x, y)
            enemy.target = player

            if tile_map:
                enemy.set_tile_map(tile_map)

            game_world.add_object(enemy, 1)  # Layer 1에 추가
            enemies.append(enemy)
            print(f"  - Spawned {enemy_class.__name__} at ({x}, {y}) [offset: {y_offset}]")

        print(f"Stage {stage_num}: Loaded {len(enemies)} enemies at base y={player_start_y}")
        return enemies

    @staticmethod
    def clear_all_enemies():
        # Layer 1 모든 객체 제거
        objects_to_remove = game_world.world[1].copy() if len(game_world.world) > 1 else []
        for obj in objects_to_remove:
            game_world.remove_object(obj)
        print("All enemies cleared")

