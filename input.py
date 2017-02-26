from xinput import XGamepad
from pygame.math import Vector2
from player import Player

gamepads = list(XGamepad)


# update function for input
def poll(player: list):
    XGamepad.update()
    for i in range(4):
        pad = gamepads[i]  # type: XGamepad
        if not pad.connected:
            if player[i]:
                player[i] = None
            continue
        else:
            if not player[i]:
                player[i] = Player()
            player[i].player_directional(Vector2() + (pad.analog_left_x, pad.analog_left_y))
            if pad.button_a:
                player[i].jump()
            if pad.button_x:
                player[i].shoot()
