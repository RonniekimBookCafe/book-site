# -*- coding: utf-8 -*-
"""
c01lib_experiment.py  |  CORE-01 Educational Library · experiment keys (2/3/4/0, folding with 1)
Release 1.6.3

Takes EXPERIMENT_STEPS (the experiment level table) from the start file so you can
drive with the drive keys while changing the wheel motor settings with the number
keys. The keys are read by c01lib_app.py, which calls the functions here
(select_next, step, reset).

    2  Start experiment mode / pick the next value (RPM → ACCEL → BRAKE F → BRAKE T → RPM again)
    3  Lower the chosen value one level  (Level Down)
    4  Raise the chosen value one level  (Level Up)
    0  Reset everything (Reset All). When in doubt, press 0
    1  Folding the screen does the same Reset All as 0

Rules
- Experiment mode starts the first time you press 2. Until then the robot screen and
  the LOG behave as usual, and 3 or 4 changes nothing and logs "press 2 first."
- Keys 2/3/4 are accepted only while the robot is stopped: no drive key is held and
  the screen's fourth line reads READY. Values never change mid-drive.
- When 2/3/4 is accepted and the screen is folded, it opens on its own, because the
  experiment results appear on the robot screen.
- A value changed with 3/4 stays as it is when you pick another value with 2, so
  you can drive with several values changed at once.
- Pressing 0, or folding the screen with 1, returns every value changed with 3/4 to
  its baseline, stops the wheels, returns them to 0°, and ends experiment mode. A
  drive key held at that moment has to be released and pressed again before the
  robot moves.

The level table lists the values for LV 1 to LV n (10 levels by default) for each
item, smallest first. The baselines are the start file's CONTROL PARAMETERS, and the
level that equals the baseline is the default level.
- If no level equals the baseline, the nearest level is replaced with the baseline
  and a NOTE appears in the console. The baseline lives only in CONTROL PARAMETERS.
- A motor-setting level outside the range of RoboCo's settings panel (e.g. Target RPM
  0-1000) is set to the nearest end of the range, with a NOTE in the console.

Official RoboCo API used
- DCMotor.max_rpm, acceleration_time, brake_force, brake_time
  (applied to the motor the moment a value is set)
"""

from .c01lib_drive import MOTOR_SETTINGS, clamp_setting
from .c01lib_log import log, ALWAYS, EVENT
from .c01lib_robot import Robot

# Experiment items: screen name → (LOG name, screen value format, target, attribute to change)
#   Target "motor": a setting on the four wheel DC Motors (the four in the default table)
#   Target "robot": a Robot steering setting (usable if you add a line to the table)
_ITEMS = {name: (en, fmt, "motor", attr) for name, (attr, fmt, en, _, _) in MOTOR_SETTINGS.items()}
_ITEMS.update({
    "STAGGER": ("Stagger",       "{:.2f} s", "robot", "steering_stagger_sec"),
    "RETURN":  ("Return time",   "{:.2f} s", "robot", "release_return_sec"),
})

# Experiment items that existed up to 1.6.0. If the level table still has one,
# the console says why it is not used.
_REMOVED_ITEMS = {
    "POWER": "wheel speed is set by RPM",
    "TORQUE": "Max Torque is fixed in the robot file",
}


def _same(a: float, b: float) -> bool:
    """Are the two values the same? (Tiny floating-point differences count as the same.)"""
    return abs(a - b) < 1e-6


class _Item:
    """One row of the level table (one value to experiment with)."""

    def __init__(self, name, base, values):
        self.name = name
        self.log_name, self.fmt, self.target, self.attr = _ITEMS[name]
        steps = [float(v) for v in values]                 # Values for LV 1 to LV n
        self.clamped = False                               # Was any level moved into the range?
        if self.target == "motor":                         # Keep inside the settings panel's range
            limited = [clamp_setting(name, v) for v in steps]
            self.clamped = limited != steps
            steps = limited
        self.base_replaced = not any(_same(v, base) for v in steps)
        if self.base_replaced:                             # No baseline: the nearest level becomes the baseline
            nearest = min(range(len(steps)), key=lambda i: abs(steps[i] - base))
            steps[nearest] = base
        self.steps = sorted(set(steps))                    # Smallest first, each value once
        self.base_level = next(i for i, v in enumerate(self.steps) if _same(v, base))
        self.level = self.base_level

    @property
    def value(self):
        return self.steps[self.level]

    @property
    def changed(self) -> bool:
        """True when 3/4 moved it to a level other than the baseline."""
        return self.level != self.base_level

    def text(self, value):
        return self.fmt.format(value)

    def lv(self):
        return f"LV {self.level + 1}/{len(self.steps)}"


class Experiment:
    """Holds the experiment level table and handles the experiment keys (2/3/4/0, folding with 1)."""

    def __init__(self, robot: Robot, steps_table):
        self.robot = robot
        self.items = []
        for name, values in steps_table:
            if name in _REMOVED_ITEMS:
                log(ALWAYS, "NOTE", f"Experiment '{name}' is no longer used - {_REMOVED_ITEMS[name]}")
                continue
            if name not in _ITEMS:
                log(ALWAYS, "NOTE", f"Unknown experiment name '{name}' - skipped")
                continue
            if not values:
                log(ALWAYS, "NOTE", f"Experiment '{name}' has no steps - skipped")
                continue
            if name in MOTOR_SETTINGS:
                base = robot.motor_settings[name]
            else:
                base = getattr(robot, _ITEMS[name][3])
            item = _Item(name, base, values)
            if item.clamped:
                low, high = MOTOR_SETTINGS[name][3], MOTOR_SETTINGS[name][4]
                log(ALWAYS, "NOTE", f"'{name}' steps outside {item.text(low)} - {item.text(high)} "
                                    f"are limited to that range")
            if item.base_replaced:
                log(ALWAYS, "NOTE", f"'{name}' steps have no {item.text(base)} (base) - "
                                    f"the nearest step is replaced, base is {item.lv()}")
            self.items.append(item)
        self.active = False       # In experiment mode? (starts the first time 2 is pressed)
        self.just_reset = False   # Showing RESET on the screen right after a reset?
        self.selected = 0

    # ------------------------------------------------------------
    # Called on every pass of the main loop
    # ------------------------------------------------------------
    def update(self):
        """Clears RESET from the screen once driving starts again after a reset."""
        if self.just_reset and self.robot.is_driving():
            self.just_reset = False
            self._show(None)

    # ------------------------------------------------------------
    # Experiment keys
    # ------------------------------------------------------------
    def _stopped(self, key: str) -> bool:
        if self.robot.is_stopped():
            return True
        log(EVENT, "EXP", f"Key {key} ignored - release drive keys and wait for READY")
        return False

    def select_next(self, key: str = "2"):
        """Key 2: starts experiment mode or picks the next value.
        Values changed earlier with 3/4 are left as they are.
        """
        if not self.items or not self._stopped(key):
            return
        self.robot.show_screen(f"key {key} - experiment screen")
        self.just_reset = False
        if not self.active:
            self.active = True
            self.selected = 0
            item = self.items[0]
            log(EVENT, "EXP", f"Experiment mode on - {item.name} ({item.log_name}) "
                              f"{item.lv()} {item.text(item.value)}")
        else:
            previous = self.items[self.selected]
            self.selected = (self.selected + 1) % len(self.items)
            item = self.items[self.selected]
            kept = (f" | {previous.name} kept at {previous.text(previous.value)}"
                    if previous.changed and previous is not item else "")
            log(EVENT, "EXP", f"Next: {item.name} ({item.log_name}) {item.lv()} "
                              f"{item.text(item.value)}{kept}")
        self._show(self.screen_text)

    def step(self, delta: int, key: str):
        """Key 3 (delta=-1) and key 4 (delta=+1): change the chosen value by one level."""
        if not self.active:
            log(EVENT, "EXP", f"Key {key} ignored - press 2 first to start experiment mode")
            return
        if not self._stopped(key):
            return
        self.robot.show_screen(f"key {key} - experiment screen")
        item = self.items[self.selected]
        new_level = item.level + delta
        if not 0 <= new_level < len(item.steps):
            edge = "lowest" if delta < 0 else "highest"
            log(EVENT, "EXP", f"{item.name} is already at the {edge} level ({item.lv()})")
            return
        old, old_level = item.value, item.level
        item.level = new_level
        self._apply(item)
        log(EVENT, "EXP", f"{item.log_name} {item.text(old)} → {item.text(item.value)} "
                          f"(LV {old_level + 1} → {item.level + 1})")
        self.robot.refresh_screen()

    def reset(self, reason: str = "key 0"):
        """Key 0, or folding the screen with key 1: reset everything. Works at any time.

        Returns every value changed with 3/4 to its baseline, stops the wheels,
        returns them to 0°, and ends experiment mode.
        reason: reason written to the console (e.g. "key 0", "key 1 - screen folded")
        """
        self.restore_all()
        self.active = False
        self.selected = 0
        self.just_reset = True
        log(ALWAYS, "EXP", f"RESET ({reason}) - all values to base, wheels stopped and back to 0°. "
                           "Release drive keys, then press again")
        self.robot.stop()        # Stop the wheels + ease the wheels back to 0°
        self._show(self.screen_text)

    def end_for_mission(self):
        """Before a mission starts, ends experiment mode and restores every value to its baseline,
        so the mission always runs on the same baseline.
        """
        changed = self.active or any(item.changed for item in self.items)
        self.restore_all()
        self.active = False
        self.just_reset = False
        self._show(None)
        if changed:
            log(EVENT, "EXP", "Experiment mode off - all values back to base for the mission")

    def restore_all(self):
        """Restores every value to its baseline (RESET, folding the screen, mission start, script end)."""
        for item in self.items:
            item.level = item.base_level
            self._apply(item)

    def _apply(self, item: _Item):
        """Applies the value to the robot immediately."""
        if item.target == "motor":
            self.robot.drive.apply_setting(item.attr, item.value)
        else:
            setattr(self.robot, item.attr, item.value)

    # ------------------------------------------------------------
    # Screen while stopped
    # ------------------------------------------------------------
    def _show(self, screen_fn):
        self.robot.idle_screen = screen_fn
        self.robot.refresh_screen()

    def screen_text(self) -> str:
        """The four Text Screen lines while stopped (9 characters or fewer per line).

            Experiment mode        Right after RESET
            RPM       value        RESET
            LV 4/10   level        KEY 0
            120 rpm   current      RPM 0
            READY     steering     READY (or STEERING)
        """
        state = "STEERING" if self.robot.is_steering() else "READY"
        if self.just_reset:
            return f"RESET\nKEY 0\nRPM 0\n{state}"
        item = self.items[self.selected]
        return f"{item.name}\n{item.lv()}\n{item.text(item.value)}\n{state}"
