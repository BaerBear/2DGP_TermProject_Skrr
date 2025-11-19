from Enemy import Knight_Sword, Knight_Bow, Knight_Tackle
import game_world

class StageManager:

    # (적 클래스, x좌표, y좌표)
    STAGE_ENEMIES = {
        0: [  # Stage0
            (Knight_Sword, 800, 256),
            (Knight_Bow, 1200, 256),
        ],
        1: [  # Stage1
            (Knight_Sword, 700, 608),
            (Knight_Bow, 1100, 608),
            (Knight_Tackle, 900, 608),
            (Knight_Sword, 1500, 608),
        ],
        2: [  # BossStage
            (Knight_Sword, 600, 512),
            (Knight_Bow, 800, 512),
            (Knight_Tackle, 1000, 512),
            (Knight_Bow, 1200, 512),
            (Knight_Sword, 1400, 512),
        ]
    }

    @staticmethod
    def load_stage_enemies(stage_num, player):
        enemies = []

        if stage_num not in StageManager.STAGE_ENEMIES:
            print(f"Warning: Stage {stage_num} has no enemy configuration")
            return enemies

        enemy_configs = StageManager.STAGE_ENEMIES[stage_num]

        for enemy_class, x, y in enemy_configs:
            enemy = enemy_class(x, y)
            enemy.target = player
            game_world.add_object(enemy, 1)
            enemies.append(enemy)
            print(f"  - Spawned {enemy_class.__name__} at ({x}, {y})")

        print(f"Stage {stage_num}: Loaded {len(enemies)} enemies")
        return enemies

    @staticmethod
    def clear_all_enemies():
        objects_to_remove = game_world.world[1].copy() if len(game_world.world) > 1 else []
        for obj in objects_to_remove:
            game_world.remove_object(obj)
        print("All enemies cleared")

    #
    # @staticmethod
    # def add_custom_enemy(stage_num, enemy_class, x, y):
    #     """
    #     특정 스테이지에 커스텀 적 추가 (런타임에서 동적 추가용)
    #
    #     Args:
    #         stage_num: 스테이지 번호
    #         enemy_class: 적 클래스 (Knight_Sword, Knight_Bow, Knight_Tackle)
    #         x, y: 배치 좌표
    #     """
    #     if stage_num not in StageManager.STAGE_ENEMIES:
    #         StageManager.STAGE_ENEMIES[stage_num] = []
    #
    #     StageManager.STAGE_ENEMIES[stage_num].append((enemy_class, x, y))
    #     print(f"Added {enemy_class.__name__} to Stage {stage_num} at ({x}, {y})")
