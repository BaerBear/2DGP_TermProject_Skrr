from Event_Checker import (
    right_down, left_down,
    attack_down, jump_down, dash_down,
    skill1_down, skill2_down, skill3_down,
    time_out, animation_end, land_on_ground, start_falling,
    combo_available, dash_complete, stop_moving
)


def Get_State_Rules(skrr):

    def land_to_idle(e):
        return land_on_ground(e) and e[1] != 'WALK'

    def land_to_walk(e):
        return land_on_ground(e) and e[1] == 'WALK'

    def dash_to_walk(e):
        return dash_complete(e) and e[1] == 'WALK'

    def dash_to_idle(e):
        return dash_complete(e) and e[1] == 'IDLE'

    def dash_to_fall(e):
        return dash_complete(e) and e[1] == 'FALL'

    def attack_to_walk(e):
        return animation_end(e) and e[1] == 'WALK'

    def attack_to_idle(e):
        return animation_end(e) and e[1] != 'WALK'

    # 스킬 전환 조건 (쿨타임 체크 포함)
    def can_use_skill1(e):
        return skill1_down(e) and skrr.is_skill_ready('skill1')

    def can_use_skill2(e):
        return skill2_down(e) and skrr.is_skill_ready('skill2')

    def can_use_skill3(e):
        return skill3_down(e) and skrr.is_skill_ready('skill3')

    def skill_to_idle(e):
        return animation_end(e) and e[1] == 'IDLE'

    def skill_to_fall(e):
        return animation_end(e) and e[1] == 'FALL'

    def skill_to_walk(e):
        return animation_end(e) and e[1] == 'WALK'

    def can_jump(e):
        return jump_down(e) and (skrr.is_grounded or skrr.jump_count < 2)

    return {
        skrr.IDLE: {
            right_down: skrr.WALK,
            left_down: skrr.WALK,
            attack_down: skrr.ATTACK,
            can_jump: skrr.JUMP,
            dash_down: skrr.DASH,
            can_use_skill1: skrr.SKILL1,
            can_use_skill2: skrr.SKILL2,
            can_use_skill3: skrr.SKILL3,
            time_out: skrr.WAIT,
        },

        skrr.WAIT: {
            right_down: skrr.WALK,
            left_down: skrr.WALK,
            attack_down: skrr.ATTACK,
            can_jump: skrr.JUMP,  # 수정
            dash_down: skrr.DASH,
            can_use_skill1: skrr.SKILL1,
            can_use_skill2: skrr.SKILL2,
            can_use_skill3: skrr.SKILL3,
            animation_end: skrr.IDLE,
        },

        skrr.WALK: {
            attack_down: skrr.ATTACK,
            can_jump: skrr.JUMP,  # 수정
            dash_down: skrr.DASH,
            can_use_skill1: skrr.SKILL1,
            can_use_skill2: skrr.SKILL2,
            can_use_skill3: skrr.SKILL3,
            stop_moving: skrr.IDLE,
        },

        skrr.JUMP: {
            can_jump: skrr.JUMP,  # 2단 점프용, 수정
            dash_down: skrr.DASH,
            attack_down: skrr.JUMPATTACK,
            can_use_skill3: skrr.SKILL3,
            start_falling: skrr.FALL,
            land_to_walk: skrr.WALK,
            land_to_idle: skrr.IDLE,
        },

        skrr.FALL: {
            can_jump: skrr.JUMP,
            dash_down: skrr.DASH,
            attack_down: skrr.JUMPATTACK,
            can_use_skill3: skrr.SKILL3,
            land_to_walk: skrr.WALK,
            land_to_idle: skrr.IDLE,
        },

        skrr.ATTACK: {
            attack_to_walk: skrr.WALK,
            attack_to_idle: skrr.IDLE,
            combo_available: skrr.ATTACK,
        },

        skrr.JUMPATTACK: {
            animation_end: skrr.FALL,
            land_to_walk: skrr.WALK,
            land_to_idle: skrr.IDLE,
        },

        skrr.DASH: {
            dash_down: skrr.DASH,
            dash_to_walk: skrr.WALK,
            dash_to_idle: skrr.IDLE,
            dash_to_fall: skrr.FALL,
        },

        skrr.DEAD: {
            animation_end: skrr.REBORN,
        },

        skrr.REBORN: {
            animation_end: skrr.IDLE,
        },

        # 스킬 State 규칙
        skrr.SKILL1: {
            skill_to_idle: skrr.IDLE,
            skill_to_fall: skrr.FALL,
            skill_to_walk: skrr.WALK,
        },

        skrr.SKILL2: {
            skill_to_idle: skrr.IDLE,
            skill_to_fall: skrr.FALL,
            skill_to_walk: skrr.WALK,
        },

        skrr.SKILL3: {
            skill_to_idle: skrr.IDLE,
            skill_to_fall: skrr.FALL,
            skill_to_walk: skrr.WALK,
        },
    }
