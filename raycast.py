from pygame.math import Vector2
from world import FIELD, IMPASSABLE


def static_collision_check(pos):
    tile_id = FIELD[int(pos.y)][int(pos.x)]
    if tile_id in IMPASSABLE:
        return True
    else:
        return False


def static_collision_raycast(start, direction, amount):
    # without points no collision
    if not start:
        return False, amount
    if amount > 1:
        pass
    delta = direction * amount
    for p in start:
        # check the start point
        if static_collision_check(p):
            return True, 0
        # check the end point
        if static_collision_check(p + delta):
            return True, amount
    return False, amount


def ray_iterator(start: Vector2, direction: Vector2, distance: float):
    stop = start + direction * distance  # type: Vector2
    return line_iterator(start, stop)


def line_iterator(start: Vector2, stop: Vector2):
    start_x = start.x
    start_y = start.y
    stop_x = stop.x
    stop_y = stop.y
    # transforming input to requirements of bresenham
    swap = abs(stop_y - start_y) > abs(stop_x - start_x)
    if swap:
        start_x, start_y = start_y, start_x
        stop_x, stop_y = stop_y, stop_x
    if start_x > stop_x:
        step_x = -1
    else:
        step_x = 1
    if start_y > stop_y:
        step_y = -1
    else:
        step_y = 1
    # iteration values
    m = (stop_y - start_y) / (stop_x - start_x) * step_x  # type: float
    fy = m + start_y
    x = start_x
    y = start_y
    delta = abs(stop_x - start_x)
    while delta > 0:
        # prepare yield values
        tmp_x = x
        tmp_y = y
        if step_x is -1:
            tmp_x -= 1
        if step_y is -1:
            tmp_y -= 1
        if swap:
            tmp_x, tmp_y = tmp_y, tmp_x
        # yield next value
        yield tmp_x, tmp_y
        # check for next increment
        if step_y is -1:
            check_y = abs(y) - 1 >= abs(fy)
        else:
            check_y = abs(y) + 1 <= abs(fy)
        if check_y:
            y += step_y
        else:
            x += step_x
            delta -= 1
            fy += m
