# -*- coding: utf-8 -*-
"""
c01lib_app.py  |  CORE-01 Educational Library · connects the start file to the robot
Release 1.6.3

Takes the values and key assignments from the start file (c01_start.py), sets up
the robot, and on every pass of the main loop reads the keys and runs three modes.

    Drive mode (PART 1-3)    Drive with W/S/A/D/Z/C/Q/E; key 1 opens and folds the screen
    Experiment mode (PART 4) Starts the first time you press 2; keys 3/4 step the chosen value
    Guide mission (PART 5)   Starts with key 5; drives the route on its own, guides, and returns

    Key 0 resets everything in any mode (when in doubt, press 0).
    Folding the screen with key 1 does the same Reset All as key 0.

Rules between modes
- During the guide mission, drive keys, key 1, and keys 2/3/4 are ignored so key
  presses can't disturb a running mission. Each ignored key gets one console line.
- If you start the mission with key 5 while in experiment mode, every value is
  restored to its baseline first. The mission always runs on the same baseline.

Any value the start file does not set comes from DEFAULTS below. To override one,
add a line to the start file with the same name.
    e.g. LOG_MAX_LINES = 500
"""

from time import sleep

from inputs import Input
from scriptruntime import Runtime

from . import c01lib_log
from .c01lib_log import log, ALWAYS, EVENT
from .c01lib_robot import Robot
from .c01lib_keys import DriveKeys, pressed
from .c01lib_experiment import Experiment
from .c01lib_mission import Mission, describe_route

# Values the start file can change, with their defaults
DEFAULTS = {
    # Wheel motor settings (same scale as the DC Motor values in RoboCo's settings panel; None = robot file value)
    "TARGET_RPM": 120,               # Target wheel speed in rpm (0-1000)
    "ACCELERATION_TIME": 0.5,        # Time to reach Target RPM when starting (s, 0-10)
    "MAX_BRAKE_FORCE": 50,           # Braking force when stopping (0-1570)
    "BRAKING_TIME": 0.2,             # Time the brake takes to stop the wheels (s, 0-10)
    # Steering
    "STEERING_SETTLE_SEC": 0.5,      # Wait after turning the wheels before they start spinning (s)
    "STEERING_STAGGER_SEC": 0.3,     # Delay between turning the front wheels and the rear wheels (s)
    "STEERING_STAGGER_ORDER": "front_rear",  # "front_rear" front then rear / "diagonal" diagonal pairs
    "STAGGER_ON_RELEASE": False,     # Also stagger the steering on key release (only when RELEASE_RETURN_SEC is 0)
    "RELEASE_RETURN_SEC": 0.6,       # Time to ease the wheels back to 0° on key release (s)
    "LOOP_DELAY_SEC": 0.02,          # How often to check key input (s)
    # Screen and logging
    "GUIDE_MESSAGE": "WELCOME",      # Guide message (up to 9 characters per line, 4 lines)
    "LOG_LEVEL": 1,                  # Console log detail (0/1/2)
    "LOG_MAX_LINES": 200,            # Maximum number of console log lines
    "TEXT_SCREEN_FONT_SIZE": None,   # Robot screen font size (None = size set in the robot file)
    # Key assignments
    "DRIVE_KEYS": {"w": "forward", "s": "backward", "a": "turn_left", "d": "turn_right",
                   "z": "rotate_left", "c": "rotate_right", "q": "diagonal_left", "e": "diagonal_right"},
    "COMMAND_KEYS": {"1": "toggle_screen", "0": "reset", "2": "next_parameter",
                     "3": "level_down", "4": "level_up", "5": "start_mission"},
    # PART 4 experiments
    "EXPERIMENT_STEPS": [],
    # PART 5 guide mission
    "MISSION_ROUTE": [],
    "GUIDE_SEC": 3.0,                # How long to open the screen and guide at the guide point (s)
    "STEP_PAUSE_SEC": 0.5,           # Pause between one action and the next (s)
    "RETURN_TO_START": True,         # Whether to retrace the route back to the start point after guiding
}

# Values that existed up to 1.6.0. If the start file still has one, the console says why it is not used.
_REMOVED = {
    "MOTOR_POWER_RATIO": "wheel speed is set by TARGET_RPM",
    "TURN_POWER_RATIO": "wheel speed is set by TARGET_RPM",
    "PIVOT_POWER_RATIO": "wheel speed is set by TARGET_RPM",
    "MAX_TORQUE": "Max Torque is fixed in the robot file",
}

# Actions you can assign to keys, with the short names shown in the console
_DRIVE_ACTIONS = {"forward": "forward", "backward": "back", "turn_left": "turn left",
                  "turn_right": "turn right", "rotate_left": "rotate left",
                  "rotate_right": "rotate right", "diagonal_left": "diag left",
                  "diagonal_right": "diag right"}
_COMMANDS = ("toggle_screen", "reset", "next_parameter", "level_down", "level_up", "start_mission")


class RobotApp:
    """Sets up the robot from the start file's values and advances the main loop one pass at a time."""

    def __init__(self, script_values: dict):
        """script_values: the start file's globals(). Only names in UPPER CASE are read."""
        s = dict(DEFAULTS)
        unknown = []
        for name, value in script_values.items():
            if name.isupper() and not name.startswith("_"):
                if name in DEFAULTS:
                    s[name] = value
                else:
                    unknown.append(name)
        self.loop_delay = s["LOOP_DELAY_SEC"]

        c01lib_log.configure(level=s["LOG_LEVEL"], max_lines=s["LOG_MAX_LINES"])
        c01lib_log.header("CORE-01 Robot 2 (Book-CORE-01-SCRIPT) | c01_start.py")
        for name in unknown:
            if name in _REMOVED:
                log(ALWAYS, "NOTE", f"'{name}' is no longer used - {_REMOVED[name]}")
            else:
                log(ALWAYS, "NOTE", f"Unknown setting '{name}' - check the spelling (it is not used)")

        self.robot = Robot(target_rpm=s["TARGET_RPM"],
                           acceleration_time=s["ACCELERATION_TIME"],
                           max_brake_force=s["MAX_BRAKE_FORCE"],
                           braking_time=s["BRAKING_TIME"],
                           steering_settle_sec=s["STEERING_SETTLE_SEC"],
                           steering_stagger_sec=s["STEERING_STAGGER_SEC"],
                           steering_stagger_order=s["STEERING_STAGGER_ORDER"],
                           stagger_on_release=s["STAGGER_ON_RELEASE"],
                           release_return_sec=s["RELEASE_RETURN_SEC"],
                           text_screen_font_size=s["TEXT_SCREEN_FONT_SIZE"],
                           guide_message=s["GUIDE_MESSAGE"])
        self.robot.setup()

        self.drive_keys = DriveKeys(self._drive_actions(s["DRIVE_KEYS"]))
        self.command_keys = self._command_streams(s["COMMAND_KEYS"], s["DRIVE_KEYS"])
        self._log_keys(s["DRIVE_KEYS"])
        self.robot.log_settings()

        self.experiment = Experiment(self.robot, s["EXPERIMENT_STEPS"])
        self.mission = Mission(self.robot, s["MISSION_ROUTE"], s["GUIDE_SEC"],
                               s["STEP_PAUSE_SEC"], s["RETURN_TO_START"])
        if s["MISSION_ROUTE"]:
            log(ALWAYS, "SETUP", f"Route {describe_route(s['MISSION_ROUTE'])} | guide {s['GUIDE_SEC']:.1f}s"
                                 f" | return {'on' if s['RETURN_TO_START'] else 'off'}")

        # Ask RoboCo to run the wrap-up code (shutdown) even when the script is stopped.
        Runtime.require_force_close()

    # ------------------------------------------------------------
    # Setup: check the key assignments
    # ------------------------------------------------------------
    def _drive_actions(self, drive_keys: dict) -> dict:
        actions = {}
        for key, name in drive_keys.items():
            if name in _DRIVE_ACTIONS:
                actions[key] = getattr(self.robot, name)
            else:
                log(ALWAYS, "NOTE", f"DRIVE_KEYS '{key}': unknown action '{name}' - skipped")
        return actions

    def _command_streams(self, command_keys: dict, drive_keys: dict) -> dict:
        streams = {}
        for key, name in command_keys.items():
            if name not in _COMMANDS:
                log(ALWAYS, "NOTE", f"COMMAND_KEYS '{key}': unknown command '{name}' - skipped")
            elif key in drive_keys:
                log(ALWAYS, "NOTE", f"COMMAND_KEYS '{key}' is already a drive key - skipped")
            else:
                streams[name] = (key, Input.stream(key))
        return streams

    def _log_keys(self, drive_keys: dict):
        k = {name: key.upper() for name, (key, _) in self.command_keys.items()}
        drive = " · ".join(f"{key.upper()} {_DRIVE_ACTIONS[name]}"
                           for key, name in drive_keys.items() if name in _DRIVE_ACTIONS)
        log(ALWAYS, "KEYS", f"{drive} · {k.get('toggle_screen', '-')} screen (fold = reset) · {k.get('reset', '-')} reset")
        log(ALWAYS, "KEYS", f"Experiment (PART 4): {k.get('next_parameter', '-')} next value · "
                            f"{k.get('level_down', '-')} level down · {k.get('level_up', '-')} level up"
                            f" | Mission (PART 5): {k.get('start_mission', '-')} start")

    # ------------------------------------------------------------
    # Repeat: main loop
    # ------------------------------------------------------------
    def running(self) -> bool:
        """True until the script is stopped."""
        return not Runtime.quitting()

    def update(self):
        """Called on every pass of the main loop. Reads the keys and advances the robot, experiment, and mission by one step."""
        try:
            self._update()
            sleep(self.loop_delay)
        except Exception as error:
            # Even on an error, restore the baseline values and stop the motors, then report it in the LOG and on the screen.
            self.mission.runner.stop()
            self.experiment.restore_all()
            self.robot.stop()
            self.robot.show_error()
            log(ALWAYS, "ERROR", f"{type(error).__name__}: {error} - motors stopped, script halted")
            raise  # Also show the Python error message (traceback) as is

    def _update(self):
        mission = self.mission.running

        # 0: reset everything (in any mode)
        if self._pressed("reset"):
            key = self.command_keys["reset"][0]
            self.mission.stop(key)
            self.experiment.reset(f"key {key}")
            self.drive_keys.clear()      # A drive key that was held must be released and pressed again to move
            mission = False

        # 2/3/4: PART 4 experiment keys
        for name, run in (("next_parameter", self.experiment.select_next),
                          ("level_down", lambda key: self.experiment.step(-1, key)),
                          ("level_up", lambda key: self.experiment.step(+1, key))):
            if self._pressed(name):
                key = self.command_keys[name][0]
                if mission:
                    self._blocked(key)
                else:
                    run(key)
        self.experiment.update()

        # 5: start the PART 5 guide mission
        if self._pressed("start_mission"):
            key = self.command_keys["start_mission"][0]
            if not self.mission.running and self.robot.is_stopped():
                self.experiment.end_for_mission()
            self.mission.start(key)
            mission = self.mission.running

        # Drive keys (ignored during the mission)
        self.drive_keys.update(self.robot.stop, blocked=self._blocked if mission else None)

        # 1: open or fold the screen (ignored during the mission). Folding does the same Reset All as key 0
        if self._pressed("toggle_screen"):
            key = self.command_keys["toggle_screen"][0]
            if mission:
                self._blocked(key)
            else:
                self.robot.toggle_screen()
                if not self.robot.screen.is_target_deployed():   # Just folded
                    self.experiment.reset(f"key {key} - screen folded")
                    self.drive_keys.clear()  # A drive key held now must be released and pressed again

        self.mission.update()
        self.robot.update()

    def _pressed(self, name: str) -> bool:
        return name in self.command_keys and pressed(self.command_keys[name][1])

    def _blocked(self, key: str):
        log(EVENT, "STATE", f"Key {key.upper()} ignored - mission is running")

    # ------------------------------------------------------------
    # Wrap-up
    # ------------------------------------------------------------
    def shutdown(self):
        """Called when the script stops. Restores the baseline values and stops the motors."""
        if self.mission.running:
            self.mission.runner.stop()
            self.robot.hide_guide()
        self.experiment.restore_all()
        self.robot.stop()
        log(ALWAYS, "END", "Script stopped - motors off, settings restored")
