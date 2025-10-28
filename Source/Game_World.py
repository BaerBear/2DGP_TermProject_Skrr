# layer 0 = 배경
# layer 1 = 몬스터
# layer 2 = 플레이어
world = [ [], [], [] ]

def add_object(obj, layer):
    world[layer].append(obj)

def update():
    for layer in world:
        for obj in layer:
            obj.update()

def render():
    for layer in world:
        for obj in layer:
            obj.draw()

def remove_object(obj):
    for layer in world:
        if obj in layer:
            layer.remove(obj)
            return