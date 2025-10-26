from pico2d import *
from Image_Loader import SKRR_Image_Loader
from State_Machine import StateMachine
from SKRR_State import Idle, Wait, Walk, Jump, JumpAttack, Attack, Dash, Fall, Dead, Reborn
from SKRR_State_Rules import Get_State_Rules


class SKRR:
    def __init__(self):
        self.x, self.y = get_canvas_width() // 2, get_canvas_height() // 2
        self.frame = 0
        self.face_dir = 1
        self.scale = 2

        self.key_pressed = {'left': False, 'right': False}
        self.is_moving = False
        self.is_grounded = True
        self.jumping = False
        self.jump_count = 0



        self.attack_type = None
        self.jumpattack_cooldown = 0

        self.dash_type = None
        self.dash_cooldown = 0

        # Image Load
        self.Idle_image = SKRR_Image_Loader('Idle').images
        self.Wait_image = SKRR_Image_Loader('Wait').images
        self.Walk_image = SKRR_Image_Loader('Walk').images
        self.AttackA_image = SKRR_Image_Loader('AttackA').images
        self.AttackB_image = SKRR_Image_Loader('AttackB').images
        self.Jump_image = SKRR_Image_Loader('Jump').images
        self.JumpEffect_image = SKRR_Image_Loader('JumpEffect').images
        self.JumpAttack_image = SKRR_Image_Loader('JumpAttack').images
        self.Reborn_image = SKRR_Image_Loader('Reborn').images
        self.Dash_image = SKRR_Image_Loader('Dash').images
        self.Fall_image = SKRR_Image_Loader('Fall').images
        self.Dead_image = SKRR_Image_Loader('Dead').images

        # State
        self.IDLE = Idle(self)
        self.WAIT = Wait(self)
        self.WALK = Walk(self)
        self.JUMP = Jump(self)
        self.JUMPATTACK = JumpAttack(self)
        self.ATTACK = Attack(self)
        self.DASH = Dash(self)
        self.FALL = Fall(self)
        self.DEAD = Dead(self)
        self.REBORN = Reborn(self)

        self.state_machine = StateMachine(self.IDLE, Get_State_Rules(self))

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()

    def handle_event(self, event):
        self.state_machine.handle_event(event)