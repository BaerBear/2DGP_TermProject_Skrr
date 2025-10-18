import os
from pico2d import load_image

class SKRR_Image_Loader:
    def __init__(self, state):
        self.images = []
        self.resource_path = os.path.join(os.path.dirname(__file__), r'..\2DGP_TermProject_Skrr\Resources\Image\Object', 'Skul')
        if state == 'Idle':
            for i in range(4):
                self.images.append(load_image(os.path.join(self.resource_path, r'Idle', f'Idle_{i}.png')))
