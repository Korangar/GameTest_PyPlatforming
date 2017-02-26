from pygame.math import Vector2


def ray_iterator(start: Vector2, direction: Vector2, distance: float):
    stop = direction * distance  # type: Vector2
    return line_iterator(start, stop)


def line_iterator(start: Vector2, stop: Vector2):
    start_x, start_y = start  # type: float
    stop_x, stop_y = stop  # type: float
    # transforming input to requirements of bresenham
    swap = abs(stop_y - start_y) > abs(stop_x - start_x)
    if swap:
        start_x, start_y = start_y, start_x
        stop_x, stop_y = stop_y, stop_x
    inverse_x = start_x > stop_x
    if inverse_x:
        step_x = -1
    else:
        step_x = 1
    inverse_y = start_y > stop_y
    if inverse_y:
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
        if inverse_x:
            tmp_x -= 1
        if inverse_y:
            tmp_y -= 1
        if swap:
            yield tmp_y, tmp_x
        else:
            yield tmp_x, tmp_y
        # check for next increment
        if inverse_y:
            check_y = abs(y) - 1 >= abs(fy)
        else:
            check_y = abs(y) + 1 <= abs(fy)
        if check_y:
            y += step_y
        else:
            x += step_x
            delta -= 1
            fy += m
