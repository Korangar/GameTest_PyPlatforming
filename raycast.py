from pygame.math import Vector2
from world import FIELD, IMPASSABLE


def static_collision_check(vector: Vector2):
    tile_id = FIELD[int(vector.y)][int(vector.x)]
    if tile_id in IMPASSABLE:
        return True
    else:
        return False


def bulk_check(node: [Vector2], direction: Vector2, amount: float):
    # without points no collision
    if not node:
        return False, amount
    direction.normalize_ip()
    for p in node:
        for v, amount in vector_ray_iterator(p, direction, amount):
            if static_collision_check(v):
                return True, amount
    return False, amount


def vector_ray_iterator(start: Vector2, direction: Vector2, distance: float):
    i = 0
    delta = Vector2()+start
    while i < distance:
        yield delta, i
        # it has to be this way or else the values will be set to the same instance of vector.
        # as the yield is by reference this retroactively will change all the previously yielded values.
        # FeelsBadMan
        delta = delta + direction
        i += 1
    yield start + direction * distance, distance


def bresenham_ray_iterator(start: Vector2, direction: Vector2, distance: float):
    yield from bresenham_line_iterator(start, start + direction * distance)


def bresenham_line_iterator(start, stop):
    start_x, start_y = start
    stop_x, stop_y = stop

    steep = abs(stop_y - start_y) > abs(stop_x - start_x)
    if steep:
        start_x, start_y = start_y, start_x
        stop_y, stop_x = stop_x, stop_y
    invert_x = stop_x < start_x
    if invert_x:
        start_x = -start_x
        stop_x = -stop_x
    delta_x = stop_x - start_x
    delta_y = abs(stop_y - start_y)
    error = 0
    y = start_y
    if start_y < stop_y:
        ystep = 1
    else:
        ystep = -1
    x = start_x
    while x <= stop_x:
        rx = x
        if invert_x:
            rx = -rx
        if steep:
            yield Vector2() + (y, rx), x
        else:
            yield Vector2() + (rx, y), x
        error += delta_y
        if 2 * error >= delta_x:
            y += ystep
            error -= delta_x
        x += 1
