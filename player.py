from pygame.math import Vector2
from world import FIELD, IMPASSABLE, SAFE
import timing

# character animation states
STAND = 0
STAND_LEDGE = 1
WALK = 10
DASH = 11
JUMP = 20
FALL = 21

# state logic groupings
STATES_JUMPABLE = [STAND, STAND_LEDGE, WALK, DASH, FALL]
STATES_APPLY_GRAVITY = [JUMP, FALL]

# raycast vectors and collision nodes
RC_AXIS_x = Vector2()+(1, 0)
RC_AXIS_y = Vector2()+(0, 1)
RC_POINTS_left = [Vector2()+(0, 0.9), Vector2()+(0, 0), Vector2()+(0, -0.9)]
RC_POINTS_right = [Vector2()+(1, 0.9), Vector2()+(1, 0), Vector2()+(1, -0.9)]
RC_POINTS_top = [Vector2()+(0.1, -1), Vector2()+(0.9, -1)]
RC_POINTS_bottom = [Vector2()+(0.1, +1), Vector2()+(0.9, +1)]
RC_POINT_GROUNDED = Vector2()+(0.5, +1)

# movement constants
const_VELOCITY_max = 90
const_GRAVITY = 50
const_JUMP = -25
const_RUN = 12


def static_colision_tile_snap(value, move):
    if move < 0:
        return int(value + move + 1)
    elif move > 0:
        return int(value + move)
    else:
        return int(value)


def static_collision_check(pos):
    tile_id = FIELD[int(pos.y)][int(pos.x)]
    if tile_id in IMPASSABLE:
        return True
    else:
        return False


def static_collision_raycast(start, direction, amount):
    # without points no collision
    if not len(start) > 0:
        return False, amount
    i = 0
    # check in bitesized steps
    while i < amount:
        delta = direction * i  # type: Vector2
        # for every collision point
        for p in start:
            if static_collision_check(p + delta):
                return True, i
        i += 1
    # check the end point
    delta = direction * amount
    for p in start:
        if static_collision_check(p + delta):
            return True, amount
    return False, amount


class PlayerEntity:
    def __init__(self):
        self.state = STAND
        self.position = Vector2() + SAFE
        self.velocity = Vector2() + (0.0, 0.0)
        self.acceleration = Vector2() + (0.0, 90.0)
        self.field = FIELD
        # when input commands are passed into update this can be none
        self.events = []

    # input commands
    def player_directional(self, stick_input):
        if stick_input.x != 0:
            self.velocity.x = stick_input.x * const_RUN
            if abs(self.velocity.x) > 0 and self.state in [STAND, STAND_LEDGE]:
                self.events.append("run")
        else:
            self.velocity.x = 0

    def jump(self):
        if self.state in STATES_JUMPABLE:
            self.state = JUMP
            self.velocity[1] = const_JUMP
            self.events.append("jump")

    def shoot(self):
        self.field[int(self.position.y) + 1][int(self.position.x)] = 0

    # update functions
    def physics_update(self):
        # apply acceleration
        self.velocity += self.acceleration * timing.delta_time
        # bound the x value
        if self.velocity .x > const_VELOCITY_max:
            self.velocity .x = const_VELOCITY_max
        elif self.velocity .x < -const_VELOCITY_max:
            self.velocity .x = -const_VELOCITY_max
        # bound the y value
        if self.velocity .y > const_VELOCITY_max:
            self.velocity .y = const_VELOCITY_max
        elif self.velocity .y < -const_VELOCITY_max:
            self.velocity .y = -const_VELOCITY_max

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
        # determine maximal distance player can move without collision
        collision, distance = static_collision_raycast(rc_start, RC_AXIS_x, speed.x)
        if collision:
            # move and snap to tile
            self.position.x = static_colision_tile_snap(self.position.x, distance)
            self.velocity .x = 0
        else:
            # move unrestricted
            self.position.x += distance
        # determine collision points
        if speed.y > 0:
            rc_start = [self.position + OFFSET for OFFSET in RC_POINTS_bottom]
        elif speed.y < 0:
            rc_start = [self.position + OFFSET for OFFSET in RC_POINTS_top]
        else:
            rc_start = []
        # check y direction
        collision, distance = static_collision_raycast(rc_start, RC_AXIS_y, speed.y)
        if collision:
            # move and snap to tile
            self.position.y = static_colision_tile_snap(self.position.y, distance)
            self.velocity .y = 0
        else:
            # move unrestricted
            self.position.y += distance

    def state_check_and_update(self):
        # check for footing
        good_footing = static_collision_check(self.position + RC_POINT_GROUNDED)
        if good_footing:
            footing = True
            if self.velocity .x == 0:
                self.state = STAND
            else:
                self.state = WALK
        else:
            footing = False
            for off in RC_POINTS_bottom:
                if static_collision_check(self.position + off):
                    footing = True
                    break
        # apply falling state if not jumping
        if not footing and not self.state == JUMP:
            self.state = FALL

    def update(self):
        # update physical variables
        self.physics_update()
        # move player
        self.safe_move()
        # update state and check environment
        self.state_check_and_update()
