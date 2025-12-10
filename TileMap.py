import xml.etree.ElementTree as ET
from pico2d import *
import os

class TileMap:
    def __init__(self, tmx_file_path):
        self.tmx_file_path = tmx_file_path
        self.tilesets = []
        self.layers = []
        self.tile_width = 0
        self.tile_height = 0
        self.map_width = 0
        self.map_height = 0
        self.tileset_images = {}
        self.collision_tiles = []  # 충돌 타일 바운딩 박스 저장
        self.camera = None  # 카메라 참조

        self.load_tmx()
        self.build_collision_boxes()

    def set_camera(self, camera):
        self.camera = camera

    def load_tmx(self):
        tree = ET.parse(self.tmx_file_path)
        root = tree.getroot()

        self.map_width = int(root.get('width'))
        self.map_height = int(root.get('height'))
        self.tile_width = int(root.get('tilewidth'))
        self.tile_height = int(root.get('tileheight'))

        base_dir = os.path.dirname(self.tmx_file_path)
        for tileset in root.findall('tileset'):
            firstgid = int(tileset.get('firstgid'))
            source = tileset.get('source')

            if source:
                tsx_path = os.path.join(base_dir, source)
                self.load_tsx(tsx_path, firstgid)
            else:
                self.load_inline_tileset(tileset, firstgid, base_dir)

        for layer in root.findall('layer'):
            layer_name = layer.get('name')
            layer_width = int(layer.get('width'))
            layer_height = int(layer.get('height'))

            data_element = layer.find('data')
            encoding = data_element.get('encoding')

            if encoding == 'csv':
                csv_data = data_element.text.strip()
                tile_ids = [int(x) for x in csv_data.replace('\n', '').split(',') if x.strip()]

                self.layers.append({
                    'name': layer_name,
                    'width': layer_width,
                    'height': layer_height,
                    'data': tile_ids
                })

    def load_tsx(self, tsx_path, firstgid):
        tree = ET.parse(tsx_path)
        root = tree.getroot()

        tile_width = int(root.get('tilewidth'))
        tile_height = int(root.get('tileheight'))
        tilecount = int(root.get('tilecount'))
        columns = int(root.get('columns'))

        image_element = root.find('image')
        if image_element is not None:
            image_source = image_element.get('source')
            image_width = int(image_element.get('width'))
            image_height = int(image_element.get('height'))

            base_dir = os.path.dirname(tsx_path)
            image_path = os.path.normpath(os.path.join(base_dir, image_source))

            if os.path.exists(image_path):
                tileset_image = load_image(image_path)

                self.tilesets.append({
                    'firstgid': firstgid,
                    'tile_width': tile_width,
                    'tile_height': tile_height,
                    'tilecount': tilecount,
                    'columns': columns,
                    'image': tileset_image,
                    'image_width': image_width,
                    'image_height': image_height
                })

    def load_inline_tileset(self, tileset_element, firstgid, base_dir):
        tile_width = int(tileset_element.get('tilewidth'))
        tile_height = int(tileset_element.get('tileheight'))
        tilecount = int(tileset_element.get('tilecount'))
        columns = int(tileset_element.get('columns'))

        image_element = tileset_element.find('image')
        if image_element is not None:
            image_source = image_element.get('source')
            image_width = int(image_element.get('width'))
            image_height = int(image_element.get('height'))

            image_path = os.path.normpath(os.path.join(base_dir, image_source))

            if os.path.exists(image_path):
                tileset_image = load_image(image_path)

                self.tilesets.append({
                    'firstgid': firstgid,
                    'tile_width': tile_width,
                    'tile_height': tile_height,
                    'tilecount': tilecount,
                    'columns': columns,
                    'image': tileset_image,
                    'image_width': image_width,
                    'image_height': image_height
                })

    def get_tileset_for_gid(self, gid):
        if gid == 0:
            return None

        for i in range(len(self.tilesets) - 1, -1, -1):
            if gid >= self.tilesets[i]['firstgid']:
                return self.tilesets[i]
        return None

    def build_collision_boxes(self):
        self.collision_tiles = []

        for layer in self.layers:
            if layer['name'] in ['tile', 'flatform']:
                for y in range(layer['height']):
                    for x in range(layer['width']):
                        index = y * layer['width'] + x
                        gid = layer['data'][index]

                        if gid != 0:
                            left = x * self.tile_width
                            bottom = (self.map_height - y - 1) * self.tile_height
                            right = left + self.tile_width
                            top = bottom + self.tile_height

                            self.collision_tiles.append({
                                'left': left,
                                'bottom': bottom,
                                'right': right,
                                'top': top - 8 if layer['name'] == 'tile' else top - 4,
                                'x': x,
                                'y': y,
                                'layer': layer['name']
                            })

    def draw_collision_boxes(self):
        if self.camera:
            camera_x, camera_y = self.camera.get_position()
        else:
            camera_x, camera_y = 0, 0

        for tile in self.collision_tiles:
            screen_left = tile['left'] - camera_x
            screen_bottom = tile['bottom'] - camera_y
            screen_right = tile['right'] - camera_x
            screen_top = tile['top'] - camera_y

            if (screen_right < 0 or screen_left > get_canvas_width() or
                screen_top < 0 or screen_bottom > get_canvas_height()):
                continue

            # 바운딩 박스 그리기
            if tile['layer'] == 'tile':
                draw_rectangle(screen_left, screen_bottom, screen_right, screen_top)
            elif tile['layer'] == 'flatform':
                draw_rectangle(screen_left, screen_bottom, screen_right, screen_top)

    def get_collision_tiles(self):
        return self.collision_tiles

    def check_collision(self, obj_left, obj_bottom, obj_right, obj_top):
        colliding_tiles = []

        for tile in self.collision_tiles:
            if (obj_left < tile['right'] and obj_right > tile['left'] and
                obj_bottom < tile['top'] and obj_top > tile['bottom']):
                colliding_tiles.append(tile)

        return colliding_tiles

    def get_bb(self):
        return 0, 0, 0, 0

    def handle_collision(self, group, other):
        pass

    def draw(self):
        for layer in self.layers:
            self.draw_layer(layer)

    def draw_layer(self, layer):
        if self.camera:
            camera_x, camera_y = self.camera.get_position()
        else:
            camera_x, camera_y = 0, 0

        from pico2d import get_canvas_width, get_canvas_height
        start_x = max(0, int(camera_x // self.tile_width))
        end_x = min(layer['width'], int((camera_x + get_canvas_width()) // self.tile_width) + 1)
        start_y = max(0, int((self.map_height * self.tile_height - camera_y - get_canvas_height()) // self.tile_height))
        end_y = min(layer['height'], int((self.map_height * self.tile_height - camera_y) // self.tile_height) + 1)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                index = y * layer['width'] + x
                gid = layer['data'][index]

                if gid == 0:
                    continue

                tileset = self.get_tileset_for_gid(gid)
                if tileset is None:
                    continue

                local_tile_id = gid - tileset['firstgid']

                tile_x = (local_tile_id % tileset['columns']) * tileset['tile_width']
                tile_y = (local_tile_id // tileset['columns']) * tileset['tile_height']

                world_x = x * self.tile_width
                world_y = (self.map_height - y - 1) * self.tile_height

                screen_x = world_x - camera_x + tileset['tile_width'] // 2
                screen_y = world_y - camera_y + tileset['tile_height'] // 2

                tileset['image'].clip_draw(
                    tile_x,
                    tileset['image_height'] - tile_y - tileset['tile_height'],
                    tileset['tile_width'],
                    tileset['tile_height'],
                    screen_x,
                    screen_y
                )

    def update(self):
        pass
