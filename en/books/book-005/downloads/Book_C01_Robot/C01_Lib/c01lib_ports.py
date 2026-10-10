# -*- coding: utf-8 -*-
"""
c01lib_ports.py  |  CORE-01 Robot 2 hardware map (Port · direction · angle)
Release 1.6.3

The target robot file is Book-CORE-01-SCRIPT (Robot 2).
Book-CORE-01-CONTROLS (Robot 1) does not use this library.

This one file collects which Port each of Robot 2's parts is connected to, which
way the motors and servos turn, and how far the steering and the screen can move.
The other c01lib_*.py files and the start file only read these values; they never
write Port numbers or angles of their own.

The values below were confirmed by running the Robot 2 that comes with the book.
Change them only if you rebuild the robot and a part ends up facing another way.

[Direction fixes go in this file only]
When a direction is wrong, do not change the key assignments or flip the angle
tables one by one. Fix motor direction only in FLIP_*_DRIVE and steering direction
only in STEERING_SIGN_*. Flipping the same axis in two places cancels out (a double
reversal), so change one axis at a time and run again to check.
"""

# ----------------------------------------------------------------
# 1. DC Motor (wheel drive) Ports
# ----------------------------------------------------------------
PORT_FR_DRIVE = 1
PORT_RR_DRIVE = 2
PORT_RL_DRIVE = 3
PORT_FL_DRIVE = 4

# ----------------------------------------------------------------
# 2. Steering Servo (wheel steering) Ports
# ----------------------------------------------------------------
PORT_FR_STEER = 5
PORT_RR_STEER = 6
PORT_RL_STEER = 7
PORT_FL_STEER = 8

# ----------------------------------------------------------------
# 3. Ports for the other parts
# ----------------------------------------------------------------
PORT_SCREEN_FOLD = 9    # Screen-Fold Servo (Small) that opens and folds the screen
PORT_TEXT_SCREEN = 10   # Text Screen
PORT_INPUT_LED = 0      # Input LED

# ----------------------------------------------------------------
# 4. Motor mounting-direction correction (MotorBase.flipped)
#    If True, flipped = True is applied to that motor at startup.
# ----------------------------------------------------------------
FLIP_FL_DRIVE = True   # Front-left wheel: turns the opposite way for the same command
FLIP_FR_DRIVE = False
FLIP_RL_DRIVE = True   # Rear-left wheel: turns the opposite way for the same command
FLIP_RR_DRIVE = False
# Why: sending spin(+) to all four wheels spins the body in place, and sending
# spin(-) to the left and spin(+) to the right drives it forward. The left and right
# motors are mounted facing each other, so only the left side turns the opposite way.
# Making this fix here, not in the key assignments, keeps W/S/A/D/Q/E true to their names.

FLIP_FL_STEER = False  # The steering servos are not flipped;
FLIP_FR_STEER = False  # their angle sign is matched with STEERING_SIGN_* below.
FLIP_RL_STEER = False
FLIP_RR_STEER = False

# ----------------------------------------------------------------
# 5. Steering-angle sign correction
#    ServoMotor.spin_to_degrees(angle): positive = CW, negative = CCW.
#    Which servo direction "+45 degrees to the right of the body" maps to depends
#    on how the servo is mounted, so each servo gets +1 or -1.
# ----------------------------------------------------------------
STEERING_SIGN_FL = -1
STEERING_SIGN_FR = -1
STEERING_SIGN_RL = -1
STEERING_SIGN_RR = -1
# Why: on this robot a positive angle turns the steering servo's wheel to the left
# (counterclockwise). The code defines "right of the body = positive," so all four
# servos get the opposite sign. If this value is wrong, pressing Q points the wheels
# to 2 o'clock instead of 10 o'clock.

# ----------------------------------------------------------------
# 6. Steering-angle limits (ServoMotor.limits_degrees, in (ccw, cw) order)
#    Diagonal moves and rotating in place need 45°, so the limit is set to 60° to
#    leave some margin. Reduce it if parts collide.
# ----------------------------------------------------------------
STEERING_LIMIT_CCW_DEG = 60.0
STEERING_LIMIT_CW_DEG = 60.0

# ----------------------------------------------------------------
# 7. Screen-Fold Servo target angles (open / folded)
# ----------------------------------------------------------------
SCREEN_FOLDED_DEG = 0.0      # Angle with the screen stowed against the body (its position right after loading the robot)
SCREEN_DEPLOYED_DEG = -90.0  # Angle with the screen opened outward from the body
# Why: going from 0° to +90° moves the screen into the body, so outward is the
# opposite direction, -90° (CCW). If it opens too little, try -100; if it opens
# too far, try something like -80.

# The limits are in (ccw, cw) order. Opening is in the CCW direction (-90°), so the CCW
# side is wide and the CW side (toward the body) is narrow. If you set SCREEN_DEPLOYED_DEG
# beyond -100, set SCREEN_FOLD_LIMIT_CCW_DEG larger than that as well.
SCREEN_FOLD_LIMIT_CCW_DEG = 100.0  # Allowed range outward (open)
SCREEN_FOLD_LIMIT_CW_DEG = 10.0    # Allowed range inward (toward the body)

# ----------------------------------------------------------------
# 8. Text Screen display limits
#    At the default font size, about 9 characters per line and 4 lines fit. Anything
#    longer wraps or pushes the lower lines off the screen. Changing the font size with
#    TEXT_SCREEN_FONT_SIZE in the start file changes these limits too.
# ----------------------------------------------------------------
SCREEN_MAX_CHARS = 9
SCREEN_MAX_LINES = 4
