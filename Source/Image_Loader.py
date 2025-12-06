import os

from pico2d import load_image


class SKRR_Image_Loader:
    def __init__(self, state):
        self.images = []
        self.resource_path = os.path.join(os.path.dirname(__file__), r'..\Resources\Image\Object', 'Skul')
        if state == 'Idle':
            for i in range(4):
                self.images.append(load_image(os.path.join(self.resource_path, r'Idle', f'Idle_{i}.png')))
        elif state == 'Wait':
            for i in range(47):
                self.images.append(load_image(os.path.join(self.resource_path, r"Wait", f'Wait_{i}.png')))
        elif state == 'Walk':
            for i in range(8):
                self.images.append(load_image(os.path.join(self.resource_path, r'Walk', f'Walk_{i}.png')))
        elif state == 'AttackA':
            for i in range(5):
                self.images.append(load_image(os.path.join(self.resource_path, r'Attack', f'AttackA_{i}.png')))
        elif state == 'AttackB':
            for i in range(4):
                self.images.append(load_image(os.path.join(self.resource_path, r'Attack', f'AttackB_{i}.png')))
        elif state == 'Jump':
            for i in range(2):
                self.images.append(load_image(os.path.join(self.resource_path, r'Jump', f'Jump_{i}.png')))
        elif state == 'JumpEffect':
            for i in range(10):
                self.images.append(load_image(os.path.join(self.resource_path, r'Jump', f'DoubleJump_Smoke_{i}.png')))
        elif state == 'JumpAttack':
            for i in range(2):
                self.images.append(load_image(os.path.join(self.resource_path, r'JumpAttack', f'JumpAttack_{i}.png')))
        elif state == 'Reborn':
            for i in range(9):
                self.images.append(load_image(os.path.join(self.resource_path, r'Reborn', f'Skill_Reborn_{i}.png')))
        elif state == 'Dash':
            self.images.append(load_image(os.path.join(self.resource_path, r'Dash', 'Dash_0.png')))
        elif state == 'DashEffect':
            for i in range(15):
                self.images.append(load_image(os.path.join(self.resource_path, r'Dash', f'Dash_Smoke_{i}.png')))
        elif state == 'Fall':
            for i in range(2):
                self.images.append(load_image(os.path.join(self.resource_path, r'Fall', f'Fall_{i}.png')))
            for i in range(3):
                self.images.append(load_image(os.path.join(self.resource_path, r'Fall', f'FallRepeat_{i}.png')))
        elif state == 'Dead':
            for i in range(3):
                self.images.append(load_image(os.path.join(self.resource_path, r'Dead', f'Fall_Dead_{i}.png')))
        elif state == 'Touch':
            for i in range(6):
                self.images.append(load_image(os.path.join(self.resource_path, r'Touch', f'Touch_{i}.png')))
        elif state == 'Skill1':
            for i in range(7):
                self.images.append(load_image(os.path.join(self.resource_path, r'Skill1', f'Skill1_{i}.png')))
        elif state == 'Skill2':
            for i in range(3):
                self.images.append(load_image(os.path.join(self.resource_path, r'Skill2', f'BuddhaCyclone_Enhanced_{i}.png')))
        elif state == 'Skill2_Effect':
            for i in range(12):
                self.images.append(load_image(os.path.join(self.resource_path, r'Skill2', f'StoneMonkey_4_BuddhaCyclone_Enhanced_{i}.png')))
        elif state == 'Skill2_Start':
            for i in range(18):
                self.images.append(load_image(os.path.join(self.resource_path, r'Skill2', f'StoneMonkey_2_BuddhaCyclone_Start_{i}.png')))
        elif state == 'Skill3_ground':
            for i in range(2):
                self.images.append(load_image(os.path.join(self.resource_path, r'Skill3', f'FlashBladeDance_Ready_{i}.png')))
            for i in range(4):
                self.images.append(load_image(os.path.join(self.resource_path, r'Skill3', f'FlashBladeDance_Attack_{i}.png')))
        elif state == 'Skill3_air':
            for i in range(2):
                self.images.append(load_image(os.path.join(self.resource_path, r'Skill3', f'FlashBladeDance_Ready_{i}.png')))
            for i in range(4):
                self.images.append(load_image(os.path.join(self.resource_path, r'Skill3', f'FlashBladeDance_Air_Attack_{i}.png')))

class Enemy_Image_Loader:
    def __init__(self, enemy_type, state):
        self.images = []
        self.resource_path = os.path.join(os.path.dirname(__file__), r'..\Resources\Image\Object', enemy_type)

        if enemy_type == 'Knight_Sword':
            if state == 'Walk':
                for i in range(8):
                    self.images.append(load_image(os.path.join(self.resource_path, f'Walk_{i}.png')))
            elif state == 'Attack':
                for i in range(5):
                    self.images.append(load_image(os.path.join(self.resource_path, f'Attack_{i}.png')))
            elif state == 'Hit':
                for i in range(2):
                    self.images.append(load_image(os.path.join(self.resource_path, f'Hit_{i}.png')))
            elif state == 'Idle':
                for i in range(6):
                    self.images.append(load_image(os.path.join(self.resource_path, f'Idle_{i}.png')))

        elif enemy_type == 'Knight_Bow':
            if state == 'Walk':
                for i in range(4):
                    self.images.append(load_image(os.path.join(self.resource_path, f'Walk_{i}.png')))
            elif state == 'Attack':
                for i in range(4):
                    self.images.append(load_image(os.path.join(self.resource_path, f'Attack_{i}.png')))
            elif state == 'Hit':
                for i in range(2):
                    self.images.append(load_image(os.path.join(self.resource_path, f'Hit_{i}.png')))
            elif state == 'Idle':
                for i in range(4):
                    self.images.append(load_image(os.path.join(self.resource_path, f'Idle_{i}.png')))
            elif state == 'Attack_Sign':
                for i in range(17):
                    self.images.append(load_image(os.path.join(self.resource_path, f'AttackSign_Archer_{i}.png')))

        elif enemy_type == 'Knight_Tackle':
            if state == 'Walk':
                for i in range(8):
                    self.images.append(load_image(os.path.join(self.resource_path, f'Walk_{i}.png')))
            elif state == 'Attack':
                for i in range(8):
                    self.images.append(load_image(os.path.join(self.resource_path, f'Attack_{i}.png')))
            elif state == 'Tackle':
                for i in range(3):
                    self.images.append(load_image(os.path.join(self.resource_path, f'Tackle_{i}.png')))
            elif state == 'Tackle_Effect':
                for i in range(9):
                    self.images.append(load_image(os.path.join(self.resource_path, f'Dash_Tackle_{i}.png')))
            elif state == 'Idle':
                for i in range(5):
                    self.images.append(load_image(os.path.join(self.resource_path, f'Idle_{i}.png')))



class Boss_Image_Loader:
    def __init__(self, boss_type, state):
        self.images = []
        self.resource_path = os.path.join(os.path.dirname(__file__), r'..\Resources\Image\Object', boss_type)

        if boss_type == 'GrimReaper':
            if state == 'Idle':
                for i in range(6):
                    self.images.append(load_image(os.path.join(self.resource_path, r'Idle', f'Idle_{i}.png')))

            elif state == 'Walk':
                for i in range(6):
                    self.images.append(load_image(os.path.join(self.resource_path, r'Walk', f'Walk_{i}.png')))

            elif state == 'Attack':
                for i in range(9):
                    self.images.append(load_image(os.path.join(self.resource_path, r'AttackA', f'AttackA_{i}.png')))

            elif state == 'Skill1_Effect':
                for i in range(32):
                    self.images.append(load_image(os.path.join(self.resource_path, r'Skill1', f'GrimReaper_Sentence_3_Hit_{i}.png')))

            elif state == 'Skill1_Motion':
                for i in range(7):
                    self.images.append(load_image(os.path.join(self.resource_path, r'Skill1', f'Skill2_1_{i}.png')))

            elif state == 'Skill2_Motion':
                for i in range(9):
                    self.images.append(load_image(os.path.join(self.resource_path, r'Skill2', f'Skill2_{i}.png')))

            elif state == 'Skill2_Fire':
                for i in range(80):
                    self.images.append(load_image(os.path.join(self.resource_path, r'Skill2', f'GrimReaper_TheStake_Land_{i}.png')))

class Effect_Image_Loader:
    def __init__(self, effect_type):
        self.images = []
        self.resource_path = os.path.join(os.path.dirname(__file__), r'..\Resources\Image\Effect', effect_type)

        if effect_type == 'Enemy_Dead':
            for i in range(6):
                self.images.append(load_image(os.path.join(self.resource_path, f'Enemy_Dead_{i}.png')))
        elif effect_type == 'Enemy_Appearance':
            for i in range(11):
                self.images.append(load_image(os.path.join(self.resource_path, f'Enemy_Appearance_{i}.png')))
        elif effect_type == 'Hit_Normal':
            for i in range(12):
                self.images.append(load_image(os.path.join(self.resource_path, f'Hit_Normal_{i}.png')))
        elif effect_type == 'Hit_Critical':
            for i in range(8):
                self.images.append(load_image(os.path.join(self.resource_path, f'Hit_Critical_{i}.png')))
        elif effect_type == 'Hit_GrimReaper':
            for i in range(15):
                self.images.append(load_image(os.path.join(self.resource_path, f'Hit_GrimReaper_{i}.png')))
        elif effect_type == 'Hit_Skill3':
            for i in range(14):
                self.images.append(load_image(os.path.join(self.resource_path, f'Hit_Ninja_{i}.png')))
        elif effect_type == 'Reward_Spawn':
            for i in range(40):
                self.images.append(load_image(os.path.join(self.resource_path, f'MapReward_Spawn_{i}.png')))
        elif effect_type == 'Skul_Hit':
            for i in range(10):
                self.images.append(load_image(os.path.join(self.resource_path, f'Skul_Hit_{i}.png')))
        elif effect_type == 'Activate':
            for i in range(80):
                self.images.append(load_image(os.path.join(self.resource_path, f'Actiavted_Loop_{i}.png')))

class Object_Image_Loader:
    def __init__(self, object_type):
        self.images = []
        self.resource_path = os.path.join(os.path.dirname(__file__), r'..\Resources\Image\Object')

        if object_type == 'Coin':
            for i in range(30):
                self.images.append(load_image(os.path.join(self.resource_path, r'Coin', f'Treasure_{i}.png')))
        elif object_type == 'Chest':
            for i in range(8):
                self.images.append(load_image(os.path.join(self.resource_path, r'Chest', f'Deactivate_{i}.png')))
        elif object_type == 'Gate_Close':
            self.images.append(load_image(os.path.join(self.resource_path, r'Gate', f'Deactivate_0.png')))
        elif object_type == 'Gate_Open':
            for i in range(8):
                self.images.append(load_image(os.path.join(self.resource_path, r'Gate', f'Activate_{i}.png')))

class UI_Image_Loader:
    def __init__(self, ui_type):
        self.images = []
        self.resource_path = os.path.join(os.path.dirname(__file__), r'..\Resources\Image\UI')

        if ui_type == 'Cursor':
            self.images.append(load_image(os.path.join(self.resource_path, 'Mouse_Cursor.png')))
        elif ui_type == 'F_key':
            self.images.append(load_image(os.path.join(self.resource_path, 'F.png')))
        elif ui_type == 'Player_Info':
            self.images.append(load_image(os.path.join(self.resource_path, 'Player_Info_UI.png')))
        elif ui_type == 'Player_HP_Bar':
            self.images.append(load_image(os.path.join(self.resource_path, 'Player_Hp_Bar.png')))