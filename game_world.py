# 0: 배경, 타일맵
# 1: 적
# 2: 플레이어
# 3: 이펙트, 투사체
# 4: UI

world = [[], [], [], [], []]
camera = None
collision_pairs = {}

def set_camera(cam):
    global camera
    camera = cam

def add_object(o, depth):
    world[depth].append(o)

def add_objects(ol, depth):
    world[depth] += ol

def remove_collision_object(o):
    for pairs in collision_pairs.values():
        if o in pairs[0]:
            pairs[0].remove(o)
        if o in pairs[1]:
            pairs[1].remove(o)

def remove_object(o):
    for layer in world:
        if o in layer:
            layer.remove(o)
            remove_collision_object(o)
            return
    print("존재하지 않는 오브젝트 제거 시도")

def update():
    # 카메라 업데이트
    if camera:
        camera.update()

    for layer in world:
        for o in layer:
            o.update()

    if len(world) > 3:
        effects_to_remove = []
        for o in world[3]:
            if hasattr(o, 'is_done') and o.is_done():
                effects_to_remove.append(o)

        for effect in effects_to_remove:
            remove_object(effect)

def render():
    for layer in world:
        for o in layer:
            o.draw()

def clear():
    for layer in world:
        layer.clear()
    collision_pairs.clear()

def collide(a, b):
    left_a, bottom_a, right_a, top_a = a.get_bb()
    left_b, bottom_b, right_b, top_b = b.get_bb()

    if left_a > right_b: return False
    if right_a < left_b: return False
    if top_a < bottom_b: return False
    if bottom_a > top_b: return False

    return True

def add_collision_pair(group, a, b):
    if group not in collision_pairs:
        collision_pairs[group] = [[], []]
    if a:
        collision_pairs[group][0].append(a)
    if b:
        collision_pairs[group][1].append(b)

def handle_collision():
    for group, pairs in collision_pairs.items():
        for a in pairs[0]:
            for b in pairs[1]:
                if collide(a, b):
                    a.handle_collision(group, b)
                    b.handle_collision(group, a)
