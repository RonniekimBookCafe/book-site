# -*- coding: utf-8 -*-
"""
c01lib_steering.py  |  CORE-01 Educational Library · the four steering servos as one group
Release 1.6.3

Handles the Steering Servos of the four wheels as one group.

- Wheel angles per posture: normal driving (0°), rotating in place (±45° per wheel),
  and diagonal left and right (all four wheels -45° / +45°), all kept in one table below.
- Staggered steering: turns two wheels first and the other two later, which keeps
  the body from twisting the way it does when all four wheels turn at once.
- Gradual steering: sends the target angle in small steps so the servos don't swing
  at once and jolt the body (used when the wheels return to 0° on key release).

Official RoboCo API used (ServoMotor)
- spin_to_degrees(angle): move to the target angle. Positive = CW, negative = CCW
- limits_degrees: allowed range of rotation, in (ccw, cw) order, both positive

Every angle in the code is "relative to the body (right = positive)." The sign
actually sent to each servo is set by c01lib_ports.STEERING_SIGN_*.
"""

from controllables import ServoMotor
from . import c01lib_ports as ports

# ----------------------------------------------------------------
# Wheel steering angle per posture (relative to the body, in °). Order: FL, FR, RL, RR
# Body-relative angles use "right = positive." The sign actually sent to each servo
# is matched by c01lib_ports.STEERING_SIGN_*, so this table keeps the designed
# angles no matter how the servos are mounted.
# ----------------------------------------------------------------
_POSTURE_ANGLES = {
    # W/S/A/D normal driving: all four wheels at 0°
    "drive": (0.0, 0.0, 0.0, 0.0),
    # Z/C rotate in place: so the four wheels roll along a circle around the body's center,
    # the two front wheels and the two rear wheels each turn 45° toward each other
    "pivot": (45.0, -45.0, -45.0, 45.0),
    # Q diagonal left: all four wheels point to 10 o'clock
    "diag_left": (-45.0, -45.0, -45.0, -45.0),
    # E diagonal right: all four wheels point to 2 o'clock
    "diag_right": (45.0, 45.0, 45.0, 45.0),
}

# ----------------------------------------------------------------
# Staggered steering order: the two wheels turned first, then the two turned later
# (wheel numbers: 0=FL, 1=FR, 2=RL, 3=RR)
#
# Turning all four wheels at once drags all four across the floor, leaving no
# wheel to hold the body in place. Turning them two at a time means fewer wheels
# drag at once, and the two wheels standing still grip the floor, which keeps
# the body from twisting as much.
# ----------------------------------------------------------------
_STAGGER_ORDERS = {
    "front_rear": ((0, 1), (2, 3)),   # Two front wheels → two rear wheels
    "diagonal": ((0, 3), (1, 2)),     # FL/RR → FR/RL (opposite diagonal pairs)
}


class SteeringServos:
    """Handles the four wheel Steering Servos as a single steering group."""

    def __init__(self):
        self.fl = ServoMotor(ports.PORT_FL_STEER)
        self.fr = ServoMotor(ports.PORT_FR_STEER)
        self.rl = ServoMotor(ports.PORT_RL_STEER)
        self.rr = ServoMotor(ports.PORT_RR_STEER)
        self._all = (self.fl, self.fr, self.rl, self.rr)
        self._signs = (ports.STEERING_SIGN_FL, ports.STEERING_SIGN_FR,
                       ports.STEERING_SIGN_RL, ports.STEERING_SIGN_RR)

        # The posture last requested, remembered so the same posture is not sent again and again.
        self._current_posture = None  # "drive" | "pivot" | "diag_left" | "diag_right"

        # In staggered steering, the remaining two wheels not yet sent
        self._pending_group = None    # Two wheel numbers
        self._pending_angles = None   # The four wheel angles for that posture
        self._pending_at = 0.0        # Time to send them

        # The angles last sent to the four wheels (body-relative). Used as the starting
        # angles for gradual steering. None if nothing has been sent yet.
        self._last_angles = [None, None, None, None]

        # Progress of gradual steering (sending the angle in steps)
        self._ramp = None             # (start angles, target angles, start time, end time)

    def apply_flip_settings(self):
        """Call once at startup to apply the servo mounting-direction correction."""
        self.fl.flipped = ports.FLIP_FL_STEER
        self.fr.flipped = ports.FLIP_FR_STEER
        self.rl.flipped = ports.FLIP_RL_STEER
        self.rr.flipped = ports.FLIP_RR_STEER

    def apply_limits(self):
        """Call once at startup to give all four servos the same allowed range of
        rotation. limits_degrees is in (ccw, cw) order, both positive.
        """
        limits = (ports.STEERING_LIMIT_CCW_DEG, ports.STEERING_LIMIT_CW_DEG)
        for servo in self._all:
            servo.limits_degrees = limits

    def _send_wheel(self, index: int, body_angle_deg: float):
        """Converts one body-relative angle to that servo's actual sign and sends it."""
        self._all[index].spin_to_degrees(body_angle_deg * self._signs[index])
        self._last_angles[index] = body_angle_deg

    def begin_posture(self, name: str, now: float,
                      second_group_delay_sec: float = 0.0,
                      order: str = "front_rear",
                      ramp_sec: float = 0.0) -> bool:
        """Changes the steering posture.

        - The two wheels that go first are steered right away.
        - The other two are steered after second_group_delay_sec.
          If that value is 0, all four wheels are steered at once.
        - order is "front_rear" (front → rear) or "diagonal" (diagonal pairs).
        - If ramp_sec is greater than 0, all four wheels steer together and the
          target angle is sent in steps over ramp_sec (no stagger in this case).
          This keeps the body from jolting when the servos swing at full speed.

        Returns False and does nothing if the posture is already the same; returns
        True if a new posture has started. True only means "started sending the
        command," not that the wheels have reached the target angle.
        """
        if name == self._current_posture:
            return False
        angles = _POSTURE_ANGLES[name]
        self._pending_group = None   # Cancel any steering left over from the previous posture
        self._ramp = None
        if ramp_sec > 0 and None not in self._last_angles:
            start = tuple(self._last_angles)
            self._ramp = (start, angles, now, now + ramp_sec)
            self._current_posture = name
            return True
        first, second = _STAGGER_ORDERS[order]
        for i in first:
            self._send_wheel(i, angles[i])
        if second_group_delay_sec > 0:
            self._pending_group = second
            self._pending_angles = angles
            self._pending_at = now + second_group_delay_sec
        else:
            for i in second:
                self._send_wheel(i, angles[i])
            self._pending_group = None
        self._current_posture = name
        return True

    def update(self, now: float):
        """Called on every pass of the main loop.
        - Staggered steering: steers the remaining two wheels when their time comes
        - Gradual steering: sends the four wheels the in-between angle for the current time
        """
        if self._pending_group is not None and now >= self._pending_at:
            for i in self._pending_group:
                self._send_wheel(i, self._pending_angles[i])
            self._pending_group = None

        if self._ramp is not None:
            start, target, t0, t1 = self._ramp
            f = 1.0 if now >= t1 else max(0.0, (now - t0) / (t1 - t0))
            # Ease the progress so the wheels start slowly and arrive slowly.
            eased = f * f * (3.0 - 2.0 * f)
            for i in range(4):
                self._send_wheel(i, start[i] + (target[i] - start[i]) * eased)
            if f >= 1.0:
                self._ramp = None
