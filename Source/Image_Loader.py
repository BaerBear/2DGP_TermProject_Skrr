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
            for i in range(26):
                self.images.append(load_image(os.path.join(self.resource_path, r'Reborn', f'Reborn1(Castle)_{i + 1}.png')))
        elif state == 'Dash':
            self.images.append(load_image(os.path.join(self.resource_path, r'Dash', 'Dash_0.png')))
        elif state == 'DashEffect':
            for i in range(15):
                self.images.append(load_image(os.path.join(self.resource_path, r'Dash', f'Dash_Smoke_{i}.png')))
        elif state == 'Fall':
            for i in range(2):
                self.images.append(load_image(os.path.join(self.resource_path, r'Fall', f'Fall_{i}.png')))
        elif state == 'Dead':
            for i in range(3):
                self.images.append(load_image(os.path.join(self.resource_path, r'Dead', f'Fall_Dead_{i}.png')))


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
                for i in range(1, 3):
                    self.images.append(load_image(os.path.join(self.resource_path, f'Hit0{i}.png')))
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
                for i in range(1, 3):
                    self.images.append(load_image(os.path.join(self.resource_path, f'Hit0{i}.png')))
            elif state == 'Idle':
                for i in range(4):
                    self.images.append(load_image(os.path.join(self.resource_path, f'Idle_{i}.png')))

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
            elif state == 'Idle':
                for i in range(5):
                    self.images.append(load_image(os.path.join(self.resource_path, f'Idle_{i}.png')))
