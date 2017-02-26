import ctypes
from enum import Enum
from time import sleep
from time import time as time_now

# XINPUT ACESS #
# Constants
NOT_CONNECTED = 1167
UBYTE = 255
CSHORT = 32767
USHORT = 65535


# Structures
class XINPUT_GAMEPAD(ctypes.Structure):
    _fields_ = [("wButtons", ctypes.c_ushort),
                ("bLeftTrigger", ctypes.c_ubyte),
                ("bRightTrigger", ctypes.c_ubyte),
                ("sThumbLX", ctypes.c_short),

                ("sThumbLY", ctypes.c_short),
                ("sThumbRX", ctypes.c_short),
                ("sThumbRY", ctypes.c_short)]


class XINPUT_STATE(ctypes.Structure):
    _fields_ = [("dwPacketNumber", ctypes.c_uint32),
                ("Gamepad", XINPUT_GAMEPAD)]


class XINPUT_VIBRATION(ctypes.Structure):
    _fields_ = [("wLeftMotorSpeed", ctypes.c_ushort),
                ("wRightMotorSpeed", ctypes.c_ushort)]

# load Xinput.dll
_xinput = ctypes.windll.xinput1_1
# getState
_XInputGetState = _xinput.XInputGetState
_XInputGetState.argtypes = [ctypes.c_uint, ctypes.POINTER(XINPUT_STATE)]
_XInputGetState.resttype = ctypes.c_uint
# setVibration
_XInputSetState = _xinput.XInputSetState
_XInputSetState.argtypes = [ctypes.c_uint, ctypes.POINTER(XINPUT_VIBRATION)]
_XInputSetState.restype = ctypes.c_uint


class XGamepad(Enum):
    gamepad0 = 0
    gamepad1 = 1
    gamepad2 = 2
    gamepad3 = 3

    @staticmethod
    def update():
        t_now = time_now()
        state = XINPUT_STATE()
        for gamepad in XGamepad:
            if gamepad.connected:
                gamepad.get_state(state)
            else:
                if gamepad.disabled:
                    pass
                elif t_now - gamepad.last_update > 5:
                    print("XGamepad checking up on {}".format(gamepad))
                    gamepad.get_state(state)

    def __init__(self, value):
        # hardware info
        self._raw_id = value
        self.connected = False
        self.disabled = False
        self.last_update = 0
        self.analog_deadzone = 0.3
        # axes
        self.analog_right_x = 0
        self.analog_right_y = 0
        self.analog_right_m = 0
        self.analog_left_x = 0
        self.analog_left_y = 0
        self.analog_left_m = 0
        self.trigger_right = 0
        self.trigger_left = 0
        # buttons
        self.shoulder_right = False
        self.shoulder_left = False
        self.button_back = False
        self.button_start = False
        self.stick_right = False
        self.stick_left = False
        self.button_a = False
        self.button_b = False
        self.button_x = False
        self.button_y = False
        self.dpad_right = False
        self.dpad_left = False
        self.dpad_down = False
        self.dpad_up = False
        # vibration
        self.vibration_right = 0
        self.vibration_left = 0

    def __repr__(self):
        return "gamepad{}".format(self._raw_id)

    def __str__(self):
        if self.connected:
            tmp = "connected"
        else:
            tmp = "not connected"
        return "gamepad{}({})".format(self._raw_id, tmp)

    def _subtract_deadzone(self, analog_axis_x: int, analog_axis_y: int):
        axis_x = analog_axis_x/CSHORT
        axis_y = analog_axis_y/CSHORT
        magnitude = (axis_x ** 2 + axis_y ** 2) ** 0.5
        if magnitude > self.analog_deadzone:
            dz_factor = (magnitude - self.analog_deadzone) / (1 - self.analog_deadzone)
            return axis_x / magnitude * dz_factor, axis_y / magnitude * dz_factor, magnitude
        else:
            return 0, 0, 0

    def _reset_input(self):
        # axes
        self.analog_right_x = 0
        self.analog_right_y = 0
        self.analog_right_m = 0
        self.analog_left_x = 0
        self.analog_left_y = 0
        self.analog_left_m = 0
        self.trigger_right = 0
        self.trigger_left = 0
        # buttons
        self.shoulder_right = False
        self.shoulder_left = False
        self.button_back = False
        self.button_start = False
        self.stick_right = False
        self.stick_left = False
        self.button_a = False
        self.button_b = False
        self.button_x = False
        self.button_y = False
        self.dpad_right = False
        self.dpad_left = False
        self.dpad_down = False
        self.dpad_up = False

    def set_vibration(self, left: float=0, right: float=0):
        self.vibration_left = left
        self.vibration_right = right
        vibration = XINPUT_VIBRATION(int(left * USHORT), int(right * USHORT))
        _XInputSetState(self._raw_id, ctypes.byref(vibration))

    def get_state(self, state=None):
        if not state:
            state = XINPUT_STATE()
        self.last_update = time_now()
        error_code = _XInputGetState(self._raw_id, state)
        if error_code == NOT_CONNECTED:
            if self.connected:
                # update connection status
                self.connected = False
                # reset input fields
                self._reset_input()
                # disconnected!
                print(self)
            # update connection status
            self.connected = False
        else:
            if not self.connected:
                # update connection status
                self.connected = True
                # deactivate vibration
                self.set_vibration()
                # reconnected!
                print(self)
            # update state and stats
            self.connected = True
            gamepad = state.Gamepad
            # update axes
            dz_x, dz_y, m = self._subtract_deadzone(gamepad.sThumbRX, gamepad.sThumbRY)
            self.analog_right_x = dz_x
            self.analog_right_y = dz_y
            self.analog_right_m = m
            dz_x, dz_y, m = self._subtract_deadzone(gamepad.sThumbLX, gamepad.sThumbLY)
            self.analog_left_x = dz_x
            self.analog_left_y = dz_y
            self.analog_left_m = m
            self.trigger_right = gamepad.bRightTrigger/UBYTE
            self.trigger_left = gamepad.bLeftTrigger/UBYTE

            def get_button(mask):
                return gamepad.wButtons & mask is not 0
            # update buttons
            self.dpad_up = get_button(0x0001)
            self.dpad_down = get_button(0x0002)
            self.dpad_left = get_button(0x0004)
            self.dpad_right = get_button(0x0008)
            self.button_start = get_button(0x0010)
            self.button_back = get_button(0x0020)
            self.stick_left = get_button(0x0040)
            self.stick_right = get_button(0x0080)
            self.shoulder_left = get_button(0x0100)
            self.shoulder_right = get_button(0x0200)
            self.button_a = get_button(0x1000)
            self.button_b = get_button(0x2000)
            self.button_x = get_button(0x4000)
            self.button_y = get_button(0x8000)

if __name__ == "__main__":
    def controller_test(pad: XGamepad):
        state = XINPUT_STATE()
        print("{} test trigger".format(pad))
        while pad.connected:
            was_pressed = pad.button_back
            pad.get_state(state)
            if pad.button_back and not was_pressed:
                break
            pad.set_vibration(pad.trigger_left, pad.trigger_right)
            yield
        print("{} test analog left {}".format(pad, pad.analog_left))
        while pad.connected:
            was_pressed = pad.button_back
            pad.get_state(state)
            if pad.button_back and not was_pressed:
                break
            print
            pad.set_vibration(abs(pad.analog_left[0]), abs(pad.analog_left[1]))
            yield
        pad.set_vibration()
        print("{} test analog right {}".format(pad, pad.analog_right))
        while pad.connected:
            was_pressed = pad.button_back
            pad.get_state(state)
            if pad.button_back and not was_pressed:
                break
            pad.set_vibration(abs(pad.analog_right[0]), abs(pad.analog_right[1]))
            yield
        pad.set_vibration()
        print("{} test buttons".format(pad))
        while pad.connected:
            was_pressed = pad.button_back
            pad.get_state(state)
            if pad.button_back and not was_pressed:
                break
            if pad.button_a:
                print("{} pressed A".format(pad))
            if pad.button_b:
                print("{} pressed B".format(pad))
            if pad.button_x:
                print("{} pressed X".format(pad))
            if pad.button_y:
                print("{} pressed Y".format(pad))
            if pad.stick_left:
                print("{} pressed left_stick".format(pad))
            if pad.stick_right:
                print("{} pressed right_stick".format(pad))
            if pad.shoulder_left:
                print("{} pressed left_shoulder".format(pad))
            if pad.shoulder_right:
                print("{} pressed right_shoulder".format(pad))
            if pad.button_back:
                print("{} pressed back".format(pad))
            if pad.button_start:
                print("{} pressed start".format(pad))
            yield
        print("{} end of test".format(pad))
    test = []
    running = True
    test_start_time = time_now()
    while running and test_start_time + 360 > time_now():
        for pad in XGamepad:
            if not pad.connected:
                pad.get_state()
                if pad.connected:
                    test.append(controller_test(pad))
        for t in test:
            try:
                next(t)
            except StopIteration:
                test = [x for x in test if x is not t]
        sleep(0.05)
    print("test exit: 360 seconds passed")
