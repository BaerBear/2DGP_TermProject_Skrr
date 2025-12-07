from pico2d import *
import common
import SKRR
from Stage_Manager import StageManager
from TileMap import TileMap
import game_framework
import game_world
import Events
import os
from Effect import create_enemy_hit_effect, create_skill3_hit_effect, create_boss_hit_effect, create_player_hit_effect

Skrr = None
tile_map = None
current_stage = 0  # 현재 스테이지 (0: Stage0, 1: Stage1, 2: BossStage)
stage_gate = None
mx, my = 0, 0

def init():
    global Skrr, tile_map, current_stage, stage_gate
    if not hide_lattice():
        hide_lattice()
    if not hide_cursor():
        hide_cursor()

    sound_manager = common.get_sound_manager()
    sound_manager.stop_bgm()
    sound_manager.play_bgm('chapter1', repeat=True)

    current_stage = 0
    tmx_path = os.path.join(os.path.dirname(__file__), '..', 'Tilemap_work', 'Stage0.tmx')
    tile_map = TileMap(tmx_path)

    Skrr = SKRR.SKRR()
    Skrr.set_tile_map(tile_map)

    camera = common.get_camera()
    camera.set_target(Skrr)
    camera.set_bounds(
        0,
        tile_map.map_width * tile_map.tile_width,
        0,
        tile_map.map_height * tile_map.tile_height
    )
    game_world.set_camera(camera)

    tile_map.set_camera(camera)

    # Layer 2: 플레이어
    game_world.add_object(Skrr, 2)

    game_world.add_collision_pair('player:tilemap', Skrr, tile_map)

    # 스테이지별 적 로드
    StageManager.load_stage_enemies(current_stage, Skrr, tile_map)

    # 게이트 생성
    stage_gate = create_stage_gate(current_stage)
    if stage_gate:
        game_world.add_object(stage_gate, 0)
        game_world.add_collision_pair('player:gate', Skrr, stage_gate)

    # 플레이어 공격 / 적의 충돌
    game_world.add_collision_pair('player_attack:enemy', Skrr, None)

    # 적 공격 / 플레이어 충돌
    game_world.add_collision_pair('enemy_attack:player', None, Skrr)


def create_stage_gate(stage_num):
    from Stage_Gate import Gate

    gate_configs = {
        0: (1450, 300, 1),  # Stage0: (x, y, next_stage)
        1: (350, 1488, 2),  # Stage1: (x, y, next_stage)
    }

    if stage_num in gate_configs:
        x, y, next_stage = gate_configs[stage_num]
        return Gate(x, y, next_stage, stage_num)
    return None

def load_stage(stage_num):
    global tile_map, current_stage, stage_gate

    stage_files = {
        0: 'Stage0.tmx',
        1: 'Stage1.tmx',
        2: 'BossStage.tmx'
    }
    Skrr.face_dir = 1
    if stage_num not in stage_files:
        return

    before_stage = current_stage
    current_stage = stage_num

    StageManager.clear_all_enemies()

    if stage_gate:
        game_world.remove_object(stage_gate)
        game_world.remove_collision_object(stage_gate)

    if tile_map:
        game_world.remove_collision_object(tile_map)

    tmx_path = os.path.join(os.path.dirname(__file__), '..', 'Tilemap_work', stage_files[stage_num])
    tile_map = TileMap(tmx_path)

    Skrr.set_tile_map(tile_map)

    # 카메라 업데이트
    camera = common.get_camera()
    camera.set_bounds(
        0,
        tile_map.map_width * tile_map.tile_width,
        0,
        tile_map.map_height * tile_map.tile_height
    )

    tile_map.set_camera(camera)

    # 충돌 페어 재설정
    game_world.add_collision_pair('player:tilemap', Skrr, tile_map)

    start_x, start_y = SKRR.stage_start_positions[stage_num]
    Skrr.x = start_x
    Skrr.y = start_y

    StageManager.load_stage_enemies(stage_num, Skrr, tile_map)

    # 게이트 생성
    stage_gate = create_stage_gate(stage_num)
    if stage_gate:
        game_world.add_object(stage_gate, 0)
        game_world.add_collision_pair('player:gate', Skrr, stage_gate)

    # BGM 변경
    sound_manager = common.get_sound_manager()
    if before_stage == 2 and stage_num != 2:
        sound_manager.stop_bgm()
        sound_manager.play_bgm('chapter1', repeat=True)
    elif current_stage == 2:
        sound_manager.stop_bgm()
        sound_manager.play_bgm('chapter1_boss', repeat=True)

    print(f"Stage {stage_num} loaded: {stage_files[stage_num]} at position ({start_x}, {start_y})")

def finish():
    game_world.clear()


def check_attack_collision():
    player = SKRR.get_player()
    if not player:
        return

    hitbox = player.get_attack_hitbox()
    if hitbox is None:
        return

    enemy_layer = 1
    if enemy_layer >= len(game_world.world):
        return

    enemies = list(game_world.world[enemy_layer])

    hitbox_left, hitbox_bottom, hitbox_right, hitbox_top = hitbox

    for enemy in enemies:
        if not player.can_hit_target(enemy):
            continue

        # 적 바운딩 박스
        if not hasattr(enemy, 'get_bb'):
            continue

        try:
            enemy_bb = enemy.get_bb()
            enemy_left, enemy_bottom, enemy_right, enemy_top = enemy_bb
        except:
            continue

        # 충돌 검사
        if (hitbox_left < enemy_right and
                hitbox_right > enemy_left and
                hitbox_bottom < enemy_top and
                hitbox_top > enemy_bottom):
            if hasattr(enemy, 'take_damage'):
                damage = player.active_hitbox.get('damage', player.attack_power)
                enemy.take_damage(damage, player.x)

                player.add_hit_target(enemy)

                enemy_center_x = (enemy_left + enemy_right) / 2
                if player.x < enemy_center_x:
                    hit_x = enemy_left
                    dir = 1
                else:
                    hit_x = enemy_right
                    dir = -1

                hit_y = (enemy_bottom + enemy_top) / 2

                current_state = player.state_machine.current_state
                if current_state == player.SKILL3:
                    create_skill3_hit_effect(hit_x, hit_y)
                else:
                    create_enemy_hit_effect(hit_x, hit_y, dir)

                is_multi_hit = player.active_hitbox.get('multi_hit', False)
                hit_interval = player.active_hitbox.get('hit_interval', 0.0)
                if enemy.type == 'Knight_Bow' or enemy.type == 'Knight_Sword' or enemy.type == 'Knight_Tackle':
                    sound_manager = common.get_sound_manager()
                    sound_manager.play_enemy_sound('enemy_hit')
                print(f"플레이어 공격 적중! 데미지: {damage} (다중 히트: {is_multi_hit}, 간격: {hit_interval}초)")


def check_player_damage():
    player = SKRR.get_player()
    if not player:
        return

    player_bb = player.get_bb()
    player_left, player_bottom, player_right, player_top = player_bb

    enemy_layer = 1
    if enemy_layer >= len(game_world.world):
        return

    enemies = list(game_world.world[enemy_layer])

    for enemy in enemies:
        if not hasattr(enemy, 'get_attack_hitbox'):
            continue

        if not enemy.can_hit_target(player):
            continue

        enemy_hitbox = enemy.get_attack_hitbox()
        if enemy_hitbox is None:
            continue

        # 충돌 검사
        hitbox_left, hitbox_bottom, hitbox_right, hitbox_top = enemy_hitbox

        if (hitbox_left < player_right and
                hitbox_right > player_left and
                hitbox_bottom < player_top and
                hitbox_top > player_bottom):

            damage = enemy.active_hitbox.get('damage', enemy.attack_power)
            if player.get_damage(damage):
                enemy.add_hit_target(player)

                player_center_x = (player_left + player_right) / 2
                if enemy.x < player_center_x:
                    hit_x = player_left
                else:
                    hit_x = player_right

                hit_y = (player_bottom + player_top) / 2

                from Boss import GrimReaper
                if isinstance(enemy, GrimReaper):
                    create_boss_hit_effect(hit_x, hit_y)
                else:
                    create_player_hit_effect(hit_x, hit_y)

                print(f"플레이어 피격! 데미지: {damage}, 남은 HP: {player.current_hp}/{player.max_hp}")


def update():
    game_world.update()
    game_world.handle_collision()
    if tile_map:
        tile_map.update()
    check_attack_collision()
    check_player_damage()

def draw():
    clear_canvas()
    if tile_map:
        tile_map.draw()

    game_world.render()

    if tile_map and game_framework.show_collision_boxes :
        tile_map.draw_collision_boxes()

    ui = common.get_ui()
    if ui and Skrr:
        ui.draw_player_info(84, 33, Skrr.current_hp, Skrr.max_hp)
        ui.draw_gold_icon(435, 33, Skrr.gold_amount)

        if stage_gate and stage_gate.player_in_range:
            camera = common.get_camera()
            if camera:
                screen_x, screen_y = camera.apply(Skrr.x, Skrr.y + Skrr.default_w + 10)
                ui.draw_f_key(screen_x, screen_y)

        global current_stage
        if current_stage == 2:
            # 보스 스테이지에서 보스 HP 표시
            from Boss import GrimReaper
            boss = None
            # Layer 1에서 보스 찾기
            if len(game_world.world) > 1:
                for obj in game_world.world[1]:
                    if isinstance(obj, GrimReaper):
                        boss = obj
                        break

            if boss and boss.is_alive:
                ui.draw_boss_hp(boss.current_hp, boss.max_hp)

        ui.draw_cursor(mx, my)

    update_canvas()

def handle_events():
    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN and e.key == SDLK_ESCAPE:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN and e.key == SDLK_f:
            # F - 게이트 상호작용
            if 'stage_gate' in globals() and stage_gate:
                stage_gate.interact()
        elif e.type == SDL_KEYDOWN and e.key == SDLK_F1:
            # F1 - 충돌 박스 표시 토글
            game_framework.show_collision_boxes = not game_framework.show_collision_boxes
        elif e.type == SDL_KEYDOWN and e.key == SDLK_F2:
            # F2 - Stage0 로드
            load_stage(0)
        elif e.type == SDL_KEYDOWN and e.key == SDLK_F3:
            # F3 - Stage1 로드
            load_stage(1)
        elif e.type == SDL_KEYDOWN and e.key == SDLK_F4:
            # F4 - BossStage 로드
            load_stage(2)
        elif e.type == SDL_MOUSEBUTTONDOWN and e.button == SDL_BUTTON_LEFT:
            print(f"Mouse Left Click: ({e.x}, {get_canvas_height() - e.y})")
        elif e.type == SDL_MOUSEMOTION:
            global mx, my
            mx, my = e.x, get_canvas_height() - e.y
        elif e.type == SDL_KEYDOWN:
            Events.handle_key_down(e, Skrr)
        elif e.type == SDL_KEYUP:
            Events.handle_key_up(e, Skrr)

def pause():
    pass

def resume():
    pass
