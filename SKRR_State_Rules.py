from Event_Checker import (
    right_down, left_down,
    attack_down, jump_down, dash_down,
    time_out, animation_end, land_on_ground, start_falling,
    combo_available, dash_complete, stop_moving
)


def get_state_rules(skrr):

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

    return {
        skrr.IDLE: {
            right_down: skrr.WALK,
            left_down: skrr.WALK,
            attack_down: skrr.ATTACK,
            jump_down: skrr.JUMP,
            dash_down: skrr.DASH,
            time_out: skrr.WAIT,
        },

        skrr.WAIT: {
            right_down: skrr.WALK,
            left_down: skrr.WALK,
            attack_down: skrr.ATTACK,
            jump_down: skrr.JUMP,
            dash_down: skrr.DASH,
            animation_end: skrr.IDLE,
        },

        skrr.WALK: {
            attack_down: skrr.ATTACK,
            jump_down: skrr.JUMP,
            dash_down: skrr.DASH,
            stop_moving: skrr.IDLE,
        },

        skrr.JUMP: {
            jump_down: skrr.JUMP,
            dash_down: skrr.DASH,  # 점프 중 대시 → DASH 상태로 (공중 대시)
            attack_down: skrr.JUMPATTACK,
            start_falling: skrr.FALL,
            land_to_walk: skrr.WALK,
            land_to_idle: skrr.IDLE,
        },

        skrr.FALL: {
            dash_down: skrr.DASH,  # 낙하 중 대시 가능
            attack_down: skrr.JUMPATTACK,
            land_to_walk: skrr.WALK,
            land_to_idle: skrr.IDLE,
        },

        skrr.ATTACK: {
            animation_end: skrr.IDLE,
            combo_available: skrr.ATTACK,
        },

        skrr.JUMPATTACK: {
            animation_end: skrr.FALL,
            land_to_walk: skrr.WALK,
            land_to_idle: skrr.IDLE,
        },

        skrr.DASH: {
            dash_down: skrr.DASH,  # 2단 대시
            dash_to_walk: skrr.WALK,
            dash_to_idle: skrr.IDLE,
            dash_to_fall: skrr.FALL,  # 공중 대시 완료 → Fall
        },

        skrr.DEAD: {
            animation_end: skrr.REBORN,
        },

        skrr.REBORN: {
            animation_end: skrr.IDLE,
        },
    }
