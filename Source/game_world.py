# 0: 배경, 타일맵
# 1: 적
# 2: 플레이어
# 3: 이펙트, 투사체
# 4: UI

world = [[], [], [], [], []]
camera = None

def set_camera(cam):
    global camera
    camera = cam

def add_object(o, depth):
    world[depth].append(o)

def add_objects(ol, depth):
    world[depth] += ol

def remove_object(o):
    for layer in world:
        if o in layer:
            layer.remove(o)
            return
    print("존재하지 않는 오브젝트 제거 시도")

def update():
    # 카메라 업데이트
    if camera:
        camera.update()

    for layer in world:
        for o in layer:
            o.update()

def render():
    for layer in world:
        for o in layer:
            o.draw()

def clear():
    for layer in world:
        layer.clear()
