from pygame.math import Vector2
from world import FIELD, SAFE
from raycast import *
import timing

# character animation states
STAND = 0
STAND_LEDGE = 1
WALK = 10
DASH = 11
AIM = 15
JUMP = 20
FALL = 21

# state logic groupings
STATES_JUMPABLE = [STAND, STAND_LEDGE, WALK, DASH, FALL]
STATES_APPLY_GRAVITY = [JUMP, FALL]
STATES_AIMABLE = [STAND, STAND_LEDGE, WALK, DASH]

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


class PlayerEntity:
    def __init__(self):
        self.state = STAND
        self.position = Vector2() + SAFE
        self.velocity = Vector2() + (0.0, 0.0)
        self.acceleration = Vector2() + (0.0, 90.0)
        self.look_direction = Vector2() + (1.0, 0.0)
        self.field = FIELD
        # when input commands are passed into update this can be none
        self.events = []

    def get_shoot_origin(self):
        if self.look_direction.x < 0:
            return self.position - (0, 0)
        else:
            return self.position + (1, 0)

    # input commands
    def enable_aiming(self, enable: bool):
        pass
        if enable and self.state in STATES_AIMABLE:
            self.velocity.x = 0
            self.state = AIM
        elif not enable and self.state is AIM:
            self.state = STAND

    def player_directional(self, stick_input: Vector2):
        if self.state is AIM:
            if stick_input.length() > 0:
                self.look_direction = stick_input.normalize()
                self.look_direction.y = -self.look_direction.y
        else:
            if stick_input.x != 0:
                self.look_direction.y = 0
                if stick_input.x > 0:
                    self.look_direction.x = 1
                else:
                    self.look_direction.x = -1
                self.velocity.x = stick_input.length() * self.look_direction.x * const_RUN
                if abs(self.velocity.x) > 0 and self.state in [STAND, STAND_LEDGE]:
                    self.events.append("run")
            else:
                self.velocity.x = 0

    def jump(self):
        if self.state in STATES_JUMPABLE:
            self.state = JUMP
            self.velocity[1] = const_JUMP
            self.events.append("jump")
            print("jump")

    def shoot(self):
        for t, i in bresenham_line_iterator(self.get_shoot_origin(), self.get_shoot_origin()+self.look_direction*30):
            if self.field[int(t.y)][int(t.x)] is not 1:
                self.field[int(t.y)][int(t.x)] = 2
            else:
                break

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
        collision, distance = bulk_check(rc_start, RC_AXIS_x, speed.x)
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
        collision, distance = bulk_check(rc_start, RC_AXIS_y, speed.y)
        if collision:
            # move and snap to tile
            self.position.y = static_colision_tile_snap(self.position.y, distance)
            self.velocity .y = 0
        else:
            # move unrestricted
            self.position.y += distance

    def state_check_and_update(self):
        # check for footing
        if static_collision_check(self.position + RC_POINT_GROUNDED):
            footing = True
            if self.state is AIM:
                pass
            elif self.velocity .x == 0:
                self.state = STAND
            else:
                self.state = WALK
        else:
            footing = False
            for off in RC_POINTS_bottom:
                if static_collision_check(self.position + off):
                    if self.state is not AIM:
                        footing = True
                        self.state = STAND_LEDGE
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
