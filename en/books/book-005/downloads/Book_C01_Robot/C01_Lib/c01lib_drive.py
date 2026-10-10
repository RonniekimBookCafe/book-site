# -*- coding: utf-8 -*-
"""
c01lib_drive.py  |  CORE-01 Educational Library · the four wheel DC motors as one group
Release 1.6.3

Handles the DC Motors of the four wheels, FL/FR/RL/RR, as one group. Each motor's
Reference is created once at startup and the same Reference is reused after that
(no new Reference for every action).

Official RoboCo API used (DCMotor)
- spin(power): spin at a power ratio, -1 to 1 (a ratio, not a physical speed unit)
- stop(): release the drive signal this code sent
- flipped: reverse the motor's direction of rotation
- max_rpm, acceleration_time, brake_force, brake_time:
  motor settings (the script reads and changes them)
- max_torque: motor setting (fixed on this robot, so it is only read)

Robot (c01lib_robot.py) never touches DCMotor directly; it only calls the functions in this file.
"""

from controllables import DCMotor
from . import c01lib_ports as ports

# Wheel speed is set by Target RPM alone.
# spin() always receives 1.0 (the full ratio), so the wheels turn up to the
# Target RPM in RoboCo's settings panel (TARGET_RPM in the script). This avoids
# setting the same speed in two places, as a ratio multiplied by an RPM.
SPIN_RATIO = 1.0

# The four motor settings the script changes.
#   screen name → (API attribute name, display format, English name, minimum, maximum)
# The English names and maximums match the names and ranges in RoboCo's settings
# panel (DC Motor). The order matches the settings panel too.
MOTOR_SETTINGS = {
    "RPM":     ("max_rpm",           "{:.0f} rpm", "Target RPM",        0.0, 1000.0),
    "ACCEL":   ("acceleration_time", "{:.2f} s",   "Acceleration Time", 0.0, 10.0),
    "BRAKE F": ("brake_force",       "{:.1f}",     "Max Brake Force",   0.0, 1570.0),
    "BRAKE T": ("brake_time",        "{:.2f} s",   "Braking Time",      0.0, 10.0),
}

# Motor settings the script does not change; it only reads and logs them.
#   screen name → (API attribute name, display format, English name)
# Max Torque is fixed at 6290 on this robot.
# Start On in the settings panel has no matching Python API property, so it is not handled.
FIXED_SETTINGS = {
    "TORQUE":  ("max_torque",        "{:.0f}",     "Max Torque"),
}


def clamp_setting(name: str, value: float) -> float:
    """Keeps a motor setting inside the range (minimum to maximum) of RoboCo's settings panel."""
    _, _, _, low, high = MOTOR_SETTINGS[name]
    return min(max(value, low), high)


class DriveMotors:
    """Handles the four wheel DC Motors as a single drive group."""

    def __init__(self):
        # Each motor's Reference is created here once and reused from then on.
        self.fl = DCMotor(ports.PORT_FL_DRIVE)
        self.fr = DCMotor(ports.PORT_FR_DRIVE)
        self.rl = DCMotor(ports.PORT_RL_DRIVE)
        self.rr = DCMotor(ports.PORT_RR_DRIVE)
        self._all = (self.fl, self.fr, self.rl, self.rr)

    def apply_flip_settings(self):
        """Call once at startup to apply the motor mounting-direction correction."""
        self.fl.flipped = ports.FLIP_FL_DRIVE
        self.fr.flipped = ports.FLIP_FR_DRIVE
        self.rl.flipped = ports.FLIP_RL_DRIVE
        self.rr.flipped = ports.FLIP_RR_DRIVE

    # ------------------------------------------------------------
    # Wheel drive patterns
    # These four patterns cover the wheel drive for all eight keys, W/S/A/D/Z/C/Q/E.
    # The wheel angle (0°, ±45°) is not handled by this class but by
    # c01lib_steering.SteeringServos.
    # All four patterns send the same SPIN_RATIO, so what differs between keys is
    # not the speed but the direction (+ / -) each wheel turns.
    # ------------------------------------------------------------
    def all_forward(self):
        """Pattern shared by W/Q/E: all four wheels forward."""
        for motor in self._all:
            motor.spin(SPIN_RATIO)

    def all_backward(self):
        """Pattern used by S: all four wheels backward."""
        for motor in self._all:
            motor.spin(-SPIN_RATIO)

    def left_back_right_forward(self):
        """Pattern shared by A/Z: left wheels backward + right wheels forward.

        A uses this pattern with the wheels at 0°, Z with the wheels at ±45°. The two
        keys differ in wheel angle, not in the motor command. The same motor command
        produces completely different motion depending on the wheel angle.
        """
        self.fl.spin(-SPIN_RATIO)
        self.rl.spin(-SPIN_RATIO)
        self.fr.spin(SPIN_RATIO)
        self.rr.spin(SPIN_RATIO)

    def left_forward_right_back(self):
        """Pattern shared by D/C: left wheels forward + right wheels backward."""
        self.fl.spin(SPIN_RATIO)
        self.rl.spin(SPIN_RATIO)
        self.fr.spin(-SPIN_RATIO)
        self.rr.spin(-SPIN_RATIO)

    def read_setting(self, name: str) -> list:
        """Reads setting `name` from all four motors and returns it in [FL, FR, RL, RR] order.
        e.g. read_setting("max_rpm")
        """
        return [getattr(motor, name) for motor in self._all]

    def apply_setting(self, name: str, value: float):
        """Sets setting `name` to `value` on all four motors. Takes effect immediately.
        e.g. apply_setting("max_rpm", 150)
        """
        for motor in self._all:
            setattr(motor, name, value)

    def target_rpm(self) -> float:
        """Returns the Target RPM currently set on the motors (read from FL; all four match).
        This is the set target, not a measured speed. Values changed with the
        experiment keys are included.
        """
        return self.fl.max_rpm

    def stop_all(self):
        """Releases the drive signal on all four wheels.

        stop() releases only the drive signals this code sent. On Robot 2
        (Book-CORE-01-SCRIPT) the Controls Mapping is not connected to the DC Motors,
        so this stop() alone is enough to stop the wheels.
        """
        for motor in self._all:
            motor.stop()
