# -*- coding: utf-8 -*-
"""
c01lib_screen.py  |  CORE-01 Educational Library · screen open/fold servo
Release 1.6.3

Toggle Screen: each press of key 1 opens or folds the screen.

It keeps the "target state" and the "actual position" apart.
- Target state: the state the script last asked for (open or folded)
- Actual position: the angle the servo is really at right now
The two can differ the moment a command is sent, because the servo needs
time to get there.
"""

from controllables import ServoMotor
from . import c01lib_ports as ports


class ScreenFold:
    """Handles the single Servo that opens and folds the screen."""

    def __init__(self, start_deployed: bool = False):
        self.servo = ServoMotor(ports.PORT_SCREEN_FOLD)
        # Target state: the state the script last asked for (True = open).
        # This can differ from whether the servo has actually reached that angle.
        self._target_deployed = start_deployed

    def apply_limits(self):
        limits = (ports.SCREEN_FOLD_LIMIT_CCW_DEG,
                 ports.SCREEN_FOLD_LIMIT_CW_DEG)
        self.servo.limits_degrees = limits

    def initialize_posture(self):
        """Called once at startup; sends the servo to the angle of the starting target state."""
        angle = ports.SCREEN_DEPLOYED_DEG if self._target_deployed else ports.SCREEN_FOLDED_DEG
        self.servo.spin_to_degrees(angle)

    def deploy(self):
        """Sets the target state to open and sends the servo to that angle."""
        self._target_deployed = True
        self.servo.spin_to_degrees(ports.SCREEN_DEPLOYED_DEG)

    def fold(self):
        """Sets the target state to folded and sends the servo to that angle."""
        self._target_deployed = False
        self.servo.spin_to_degrees(ports.SCREEN_FOLDED_DEG)

    def toggle(self):
        """Flips the target state on each press of key 1 (open ↔ folded).

        c01lib_app.py calls this function only at the moment the key is pressed,
        so holding the key down does not keep opening and folding the screen.
        """
        if self._target_deployed:
            self.fold()
        else:
            self.deploy()

    def is_target_deployed(self) -> bool:
        """Returns True if the target state is open. This is the state the script
        last asked for, not the servo's actual position.
        """
        return self._target_deployed
