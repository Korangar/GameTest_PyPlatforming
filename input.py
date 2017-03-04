from pygame.math import Vector2
from player import PlayerEntity


# update function for input
def x_poll(player: list):
    xinput.Gamepad.update()
    gamepads = list(xinput.Gamepad)
    for i in range(4):
        pad = gamepads[i]  # type: XGamepad
        if not pad.connected:
            if player[i]:
                player[i] = None
            continue
        else:
            if not player[i]:
                player[i] = PlayerEntity()

            stick_left = pad.input_state["analog_left"]  # type: xinput.AnalogStick
            player[i].player_directional(Vector2() + (stick_left.x, stick_left.y))

            trigger_right = pad.input_state["trigger_right"]
            player[i].enable_aiming(trigger_right > 0.5)

            events = pad.input_state["event"]
            if "button_a" in events and events["button_a"]:
                player[i].jump()

            if "button_x" in events and events["button_x"]:
                player[i].shoot()


def nopoll(player:list):
    pass

try:
    import xinput
    poll = x_poll
except ImportError:
    xinput = None
    poll = nopoll
