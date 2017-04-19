import timing
from raycast import *


def static_colision_tile_snap(value, move):
    if move < 0:
        return int(value + move + 1)
    elif move > 0:
        return int(value + move)
    else:
        return int(value)


def safe_move(self):
    speed = self.velocity * timing.delta_time
    # return if there is no movement happening
    if speed.length() == 0:
        return
    # determine points at which colision should be checked
    if speed.x > 0:
        rc_start = [self.position + OFFSET for OFFSET in RC_POINTS_right]
    elif speed.x < 0:
        rc_start = [self.position + OFFSET for OFFSET in RC_POINTS_left]
    else:
        rc_start = []
    # crop distance to move without collision
    collision, distance = bulk_check(rc_start, RC_AXIS_x, speed.x)
    if collision:
        # move only until collision occurs and resolve overlapping
        self.position.x = static_colision_tile_snap(self.position.x, distance)
        self.velocity .x = 0
    else:
        # move full distance unrestricted
        self.position.x += distance
    # determine collision points
    if speed.y > 0:
        rc_start = [self.position + OFFSET for OFFSET in RC_POINTS_bottom]
    elif speed.y < 0:
        rc_start = [self.position + OFFSET for OFFSET in RC_POINTS_top]
    else:
        rc_start = []
    # check y direction
    collision, distance = bulk_check(rc_start, RC_AXIS_y, speed.y)
    if collision:
        # move and snap to tile
        self.position.y = static_colision_tile_snap(self.position.y, distance)
        self.velocity .y = 0
    else:
        # move unrestricted
        self.position.y += distance


class Entity:
    def __init__(self):
        pass
