# -*- coding: utf-8 -*-
"""
c01lib_log.py  |  CORE-01 Educational Library · console LOG
Release 1.6.3

The console LOG is an event record of what happened and when.
The robot's Text Screen shows the current state (action, power, steering), so
the console only gets short lines for events that change the state.

The LOG is written in English so that it matches the robot screen, the key
names, and the RoboCo API. Read each line like this:

    [  12.34s] STEER   Pivot posture (front → rear stagger)
     ────┬────  ──┬──   ───────────────┬───────────────
     time since  category             message
     start

The category is one word in capitals.
    START  script started          KEYS   key guide
    SETUP  settings for this run   STEER  wheel posture changed
    SCREEN screen opened/folded    DRIVE  driving action summary (LOG_LEVEL 2)
    EXP    experiment value/RESET  STATE  guide mission state and step
    END    script ended            ERROR  error while running
    NOTE   notice (line limit, etc.)

LOG_LEVEL sets how much is written.
    0 : only essential lines such as START, SETUP, END, ERROR
    1 : 0 + wheel posture changes, screen changes, experiment values, mission state (default)
    2 : 1 + driving actions (one line on key release, e.g. "W forward | held 0.32s")

Lines piling up in the console can slow the run, so once LOG_MAX_LINES lines are
printed, one NOTE line is written and output stops. ERROR lines and LOG_LEVEL 0
lines are always printed regardless of this limit.
"""

from time import time as _time

_start_time = _time()
_level = 1
_max_lines = 200
_lines = 0
_stopped = False

# LOG levels (used as the level argument)
ALWAYS = 0   # Essential lines such as start, setup, and end
EVENT = 1    # Wheel posture changes, screen changes, experiment values
DETAIL = 2   # Every single driving action


def configure(level: int = 1, max_lines: int = 200):
    """Applies the start file's LOG_LEVEL and LOG_MAX_LINES values."""
    global _level, _max_lines
    _level = level
    _max_lines = max_lines


def header(title: str):
    """Prints once at startup what is running and how to read the LOG."""
    print(f"==== {title} ====")
    print(f"  time = seconds since start | LOG_LEVEL {_level} | max {_max_lines} lines")


def _stamp() -> str:
    return f"[{_time() - _start_time:7.2f}s]"


def log(level: int, category: str, message: str):
    """Writes one event line to the console.

    :param level: one of ALWAYS / EVENT / DETAIL. Not printed if higher than LOG_LEVEL
    :param category: one capitalized category word (START, KEYS, SETUP, STEER, SCREEN,
                     DRIVE, EXP, STATE, END, ERROR, NOTE)
    :param message: human-readable text (English)
    """
    global _lines, _stopped
    always = category == "ERROR" or level == ALWAYS
    if level > _level and not always:
        return
    if _stopped and not always:
        return
    print(f"{_stamp()} {category:<6}  {message}")
    _lines += 1
    if _lines >= _max_lines and not _stopped:
        _stopped = True
        print(f"{_stamp()} {'NOTE':<6}  LOG reached {_max_lines} lines - further lines are hidden "
              "(ERROR and END are still shown)")
