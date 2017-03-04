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
        delta = delta + direction
        i += 1
    yield start + direction * distance, distance


def bresenham_ray_iterator(start: Vector2, direction: Vector2, distance: float):
    yield from bresenham_line_iterator(start, start + direction * distance)


def bresenham_line_iterator(start: Vector2, stop: Vector2):
    if start == stop:
        yield Vector2()+(start.x, start.y), 0.0
        return
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
    delta = 0
    while delta < abs(stop_x - start_x):
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
        yield Vector2()+(tmp_x, tmp_y), delta
        # check for next increment
        if step_y is -1:
            check_y = abs(y) - 1 >= abs(fy)
        else:
            check_y = abs(y) + 1 <= abs(fy)
        if check_y:
            y += step_y
        else:
            x += step_x
            delta += 1
            fy += m

if __name__ == "__main__":
    start = Vector2()+(0, 0)
    direction = Vector2() + (1, 1)
    amnt = 100.0
    import timeit
    print("vector time:{}".
          format(timeit.timeit(lambda: list(vector_ray_iterator(start, direction, amnt)), number=1)))
    print("bresenham time:{}".
          format(timeit.timeit(lambda: list(bresenham_ray_iterator(start, direction, amnt)), number=1)))


    vec_result = list(vector_ray_iterator(Vector2() + (0, 0), direction, amnt))
    bres_result = list(bresenham_ray_iterator(Vector2() + (0, 0), direction, amnt))

    print(list(map((lambda t: (t[0].x, t[0].y, t[1])), vec_result)))
    print(bres_result)
