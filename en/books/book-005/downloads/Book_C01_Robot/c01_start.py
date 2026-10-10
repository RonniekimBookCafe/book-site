# -*- coding: utf-8 -*-
"""
c01_start.py  |  CORE-01 start file
Release 1.6.3  |  Connect this file to the robot file Book-CORE-01-SCRIPT (Robot 2) and run it.

This one file covers every exercise in the book.
    PART 1-3  Drive with W/S/A/D/Z/C/Q/E; key 1 opens and folds the screen
    PART 4    Keys 2/3/4 change the wheel motor settings so you can compare (experiments)
    PART 5    Key 5 starts the guide mission
    Any time  Key 0 resets everything (when in doubt, press 0)

This file only holds the values you can change and the key assignments. The code
that moves the robot lives in the library in the C01_Lib folder.
"""

# --- Setup code: do not change this part ---------------------------------------
# Every time the script runs, it reloads the C01_Lib library. That way any change
# you make to a library file takes effect right away. Nothing is deleted; this only
# clears the old copy that RoboCo kept in memory.
import sys as _sys

_sys.dont_write_bytecode = True  # Do not create temporary files (the __pycache__ folder) when running

for _mod_name in list(_sys.modules.keys()):
    if _mod_name == "Book_C01_Robot" or _mod_name.startswith("Book_C01_Robot."):
        del _sys.modules[_mod_name]

from Book_C01_Robot.C01_Lib.c01lib_app import RobotApp


# ========================================
# 1. CONTROL PARAMETERS  (values to try changing first)
# ========================================
# --- Wheel motor settings: same names and ranges as RoboCo's settings panel (DC Motor) ---
#     Applied to all four wheels when the script starts. They are the PART 4 baselines.
#     Driving speed is set by TARGET_RPM alone; all eight drive keys use the same value.
TARGET_RPM = 120             # Target wheel speed in rpm (0-1000)
ACCELERATION_TIME = 0.5      # Time to reach Target RPM when starting (seconds, 0-10)
MAX_BRAKE_FORCE = 50         # Braking force when stopping (0-1570)
BRAKING_TIME = 0.2           # Time the brake takes to stop the wheels (seconds, 0-10)
# Max Torque (6290) is fixed, so it is not changed. Start On (ON) has no matching
# Python API property. Both keep the robot file's setting.

# --- Steering: timing when the wheels change direction (seconds) ---
STEERING_SETTLE_SEC = 0.5    # Wait after turning the wheels before they start spinning
STEERING_STAGGER_SEC = 0.3   # Delay between turning the front wheels and turning the rear wheels
RELEASE_RETURN_SEC = 0.6     # Time to ease the wheels back to 0° when you release the key

# --- Screen and logging ---
GUIDE_MESSAGE = "WELCOME"    # Guide message (up to 9 characters per line, 4 lines; use "\n" for a line break)
LOG_LEVEL = 1                # Console log detail: 0 minimal · 1 normal · 2 includes driving actions


# ========================================
# 2. KEYS  (key assignments)
#    If you change a key here, set the same key in the robot file's Controls Mapping.
# ========================================
DRIVE_KEYS = {               # Act while the key is held down
    "w": "forward",          # Forward
    "s": "backward",         # Backward
    "a": "turn_left",        # Turn left
    "d": "turn_right",       # Turn right
    "z": "rotate_left",      # Rotate left in place
    "c": "rotate_right",     # Rotate right in place
    "q": "diagonal_left",    # Diagonal forward-left
    "e": "diagonal_right",   # Diagonal forward-right
}
COMMAND_KEYS = {             # Act once, the moment the key is pressed
    "1": "toggle_screen",    # Open or fold the screen (folding = Reset All, like 0)
    "0": "reset",            # Reset everything (when in doubt, press 0)
    "2": "next_parameter",   # PART 4: choose the value to test (RPM → ACCEL → BRAKE F → BRAKE T)
    "3": "level_down",       # PART 4: one level down
    "4": "level_up",         # PART 4: one level up
    "5": "start_mission",    # PART 5: start the guide mission
}


# ========================================
# 3. EXPERIMENT STEPS  (PART 4 experiment levels)
#    For each value, list LV 1 to LV 10, smallest first. LV 10 is the maximum in RoboCo's settings panel.
#    The level that equals the baseline (the value in section 1) is the default level.
#    Each press of key 2 picks the next item, top to bottom; keys 3/4 change it one level.
#    Values changed with 3/4 stay when you pick another with 2; 0 or folding with 1 restores the baselines.
# ========================================
EXPERIMENT_STEPS = [
    ("RPM",     [30, 60, 90, 120, 200, 300, 400, 600, 800, 1000]),     # TARGET_RPM (base LV 4)
    ("ACCEL",   [0.1, 0.2, 0.5, 1, 2, 3, 4, 6, 8, 10]),                # ACCELERATION_TIME (base LV 3)
    ("BRAKE F", [0, 25, 50, 100, 200, 400, 600, 900, 1200, 1570]),     # MAX_BRAKE_FORCE (base LV 3)
    ("BRAKE T", [0, 0.1, 0.2, 0.5, 1, 2, 4, 6, 8, 10]),                # BRAKING_TIME (base LV 3)
]


# ========================================
# 4. MISSION  (PART 5 guide mission)
#    List the route from the start point to the guide point as (action, seconds) pairs.
#    Actions: forward · backward · turn_left · turn_right · rotate_left · rotate_right · pause
# ========================================
MISSION_ROUTE = [
    ("forward",      2.0),   # Forward for 2 seconds
    ("rotate_right", 0.5),   # Rotate right in place for 0.5 seconds (about 90° at the baseline RPM 120, ACCEL 0.5 s)
    ("forward",      1.5),   # Forward for 1.5 seconds
]
GUIDE_SEC = 3.0              # How long to open the screen and guide at the guide point (seconds)
STEP_PAUSE_SEC = 0.5         # Pause between one action and the next (seconds)
RETURN_TO_START = True       # After guiding, retrace the same route back to the start point


# ========================================
# 5. RUN  (set up once, then repeat until stopped)
# ========================================
def main():
    app = RobotApp(globals())    # Setup: pass the values and key assignments above to the robot once
    while app.running():         # Repeat until the script is stopped
        app.update()             # Read keys -> move the robot -> update the screen and console
    app.shutdown()               # Wrap up: restore the baseline values and stop the motors


if __name__ == "__main__":
    main()
