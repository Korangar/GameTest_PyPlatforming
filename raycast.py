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
    yield from bresenham_line_iterator1(start, start + direction * distance)


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


def bresenham_line_iterator2(start: Vector2, stop: Vector2):
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


def bresenham_line_iterator1(start: Vector2, stop: Vector2):
    steep = abs(stop.y - start.y) > abs(stop.x - start.x)
    if steep:
        start.x, start.y = start.y, start.x
        stop.y, stop.x = stop.x, stop.y
    if start.x > stop.x:
        start.x, stop.x = stop.x, start.x
        start.y, stop.y = stop.y, start.y
    deltax = stop.x - start.x
    deltay = abs(stop.y - start.y)
    error = 0
    y = start.y
    if start.y < stop.y:
        ystep = 1
    else:
        ystep = -1
    x = start.x
    while x <= stop.x:
        if steep:
            yield Vector2() + (y, x), x
        else:
            yield Vector2() + (x, y), x
        error += deltay
        if 2 * error >= deltax:
            y += ystep
            error -= deltax
        x += 1


if __name__ == "__main__":
    start = Vector2()+(0, 0)
    direction = Vector2() + (1, 1)
    direction.normalize_ip()
    amnt = 100.0
    n = 1
    test1_f = vector_ray_iterator
    test2_f = bresenham_line_iterator2
    import timeit

    vec_result = list(test1_f(Vector2() + (0, 0), direction, amnt))
    bres_result = list(test2_f(Vector2() + (0, 0), direction * amnt))

    def test1():
        list(test1_f(start, direction, amnt))
    print("vector time:{}".
          format(timeit.timeit(test1, number=n)/n/len(vec_result)))

    def test2():
        test2_f(start, start + direction * amnt)
    print("bresenham time:{}".
          format(timeit.timeit(test2, number=n)/n/len(bres_result)))



    print(vec_result)
    print(bres_result)
