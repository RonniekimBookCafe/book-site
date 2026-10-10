# -*- coding: utf-8 -*-
"""
c01lib_led.py  |  CORE-01 Educational Library · Input LED color
Release 1.6.3

Changes the color of the Input LED to match what the robot is doing.

The LED's flash on a key press (Pulse) is handled by RoboCo's Controls Mapping;
this code only changes the color. That is why it never calls turn_on() or
turn_off(). On this one LED, Controls Mapping owns the Pulse and Python owns
the color.

Note: a known issue in the RoboCo API
Color.from_hex("black") returns a function instead of a Color, so writing
led.color = "black" raises an error. This file therefore uses Color(0, 0, 0)
directly whenever it needs black (a color that looks switched off).
Other color names such as "red", "green", and "white" work normally.
"""

from controllables import LED
from color import Color
from . import c01lib_ports as ports

# LED color for each action. Stopped is black, Color(0, 0, 0)
# (the name "black" is not used, for the reason above).
_STATE_COLORS = {
    "idle": Color(0, 0, 0),
    "forward": Color.green(),
    "backward": Color.red(),
    "turn_left": Color(0.0, 0.4, 1.0),
    "turn_right": Color(0.0, 0.4, 1.0),
    "pivot_left": Color(0.6, 0.0, 1.0),
    "pivot_right": Color(0.6, 0.0, 1.0),
    "diagonal_left": Color(1.0, 0.6, 0.0),
    "diagonal_right": Color(1.0, 0.6, 0.0),
}
_DEFAULT_COLOR = Color(1.0, 1.0, 1.0)  # Any action not in the table is white


class InputLED:
    """Handles only the color of a single Input LED.

    The LED's Pulse (flash) belongs to Controls Mapping, so it is not handled here.
    """

    def __init__(self):
        self.led = LED(ports.PORT_INPUT_LED)

    def set_color(self, state_name: str):
        """Sets the LED to the color for the action name (state_name).
        Names not in the table set it to white.
        """
        self.led.color = _STATE_COLORS.get(state_name, _DEFAULT_COLOR)
