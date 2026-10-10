# -*- coding: utf-8 -*-
"""
c01lib_mission.py  |  CORE-01 Educational Library · guide mission route
Release 1.6.3

Runs the guide mission. Key 5 in the start file starts it, and key 0 stops it at
any time. The mission passes through four states in order.

    WAIT → MOVE → GUIDE → RETURN → WAIT

- Mission     : the state flow (the rules for moving from one state to the next)
- RouteRunner : runs the route's actions one by one in MOVE and RETURN

The route (MISSION_ROUTE) is a list of actions and durations measured from where
the robot is standing.

    MISSION_ROUTE = [("forward", 2.0), ("rotate_right", 0.5), ("forward", 1.5)]

Each action runs in this order.

    start the action → (if the wheels must change direction, wait for steering to finish)
    → drive for the set time → stop → wait until stopped → short pause → next action

Drive time is measured from the moment the wheels actually start rolling. This
robot has no sensor that measures position, so a finished action means "moved
for the set time," not "arrived at the target point."

Nothing waits with time.sleep(), so key 0 (stop the mission) keeps being read
while the mission runs.
"""

from time import time as _now

from .c01lib_log import log, ALWAYS, EVENT
from .c01lib_robot import Robot

# Actions allowed in a route: name → (Robot action, action on the way back, screen label, LOG name)
# pause does not move; it just waits for the set time.
_ACTIONS = {
    "forward":      ("forward",      "backward",     "FORWARD",  "forward"),
    "backward":     ("backward",     "forward",      "BACKWARD", "backward"),
    "turn_left":    ("turn_left",    "turn_right",   "TURN L",   "turn left"),
    "turn_right":   ("turn_right",   "turn_left",    "TURN R",   "turn right"),
    "rotate_left":  ("rotate_left",  "rotate_right", "ROTATE L", "rotate left"),
    "rotate_right": ("rotate_right", "rotate_left",  "ROTATE R", "rotate right"),
    "pause":        (None,           "pause",        "PAUSE",    "pause"),
}


def reverse_route(route):
    """Builds the route that retraces the same path backward.
    It reverses the order and swaps each action for its opposite (forward ↔ backward,
    left ↔ right). The body keeps its heading and backs along the route.
    """
    return [(_ACTIONS[action][1], sec) for action, sec in reversed(route) if action in _ACTIONS]


def describe_route(route) -> str:
    """Writes the route on one line. e.g. forward 2.0s → rotate right 0.5s"""
    return " → ".join(f"{_ACTIONS[a][3]} {sec:.1f}s" for a, sec in route if a in _ACTIONS)


class RouteRunner:
    """Runs the route's actions one at a time, in order."""

    def __init__(self, robot: Robot, pause_sec: float = 0.5):
        self.robot = robot
        self.pause_sec = pause_sec      # Pause between one action and the next
        self.steps = []
        self.index = 0
        self.label = ""                 # Name of the state now running (MOVE / RETURN)
        self.phase = "idle"             # idle · begin · steer · drive · settle · pause · done
        self.phase_end = 0.0

    def start(self, route, label: str):
        """Starts running the route. Actions that cannot be used are skipped."""
        self.steps = []
        for action, sec in route:
            if action not in _ACTIONS:
                log(ALWAYS, "NOTE", f"Unknown route action '{action}' - skipped")
            elif sec <= 0:
                log(ALWAYS, "NOTE", f"Route action '{action}' has no time - skipped")
            else:
                self.steps.append((action, sec))
        self.index = 0
        self.label = label
        self.phase = "begin"

    def stop(self):
        """Stops running the route. Stopping the robot is the caller's job."""
        self.steps = []
        self.phase = "idle"

    @property
    def done(self) -> bool:
        """True once every action in the route is done."""
        return self.phase == "done"

    def update(self):
        """Called on every pass of the main loop. Advances the current action by one step."""
        now = _now()
        if self.phase == "begin":
            if self.index >= len(self.steps):
                self.phase = "done"
                return
            action, sec = self.steps[self.index]
            method, _, _, name = _ACTIONS[action]
            log(EVENT, "STATE", f"{self.label} step {self.index + 1}/{len(self.steps)}: {name} {sec:.2f}s")
            if method is None:                      # pause: wait without moving
                self.phase, self.phase_end = "pause", now + sec
            else:
                getattr(self.robot, method)()       # Starts with steering first if needed
                self.phase = "steer"
            self.robot.refresh_screen()
        elif self.phase == "steer":
            if not self.robot.is_steering():        # Time from the moment the wheels start rolling
                self.phase, self.phase_end = "drive", now + self.steps[self.index][1]
        elif self.phase == "drive":
            if now >= self.phase_end:
                self.robot.stop()                   # Stop the wheels + return the wheels to 0°
                self.phase = "settle"
        elif self.phase == "settle":
            if self.robot.is_stopped():
                self.phase, self.phase_end = "pause", now + self.pause_sec
        elif self.phase == "pause":
            if now >= self.phase_end:
                self.index += 1
                self.phase = "begin"

    def screen_text(self, state: str) -> str:
        """The four Text Screen lines during the mission (9 characters or fewer per line).

            MOVE        current state (MOVE / GUIDE / RETURN)
            STEP 2/3    current step
            ROTATE R    current action
            STEERING    steering state (READY / STEERING)
        """
        steer = "STEERING" if self.robot.is_steering() else "READY"
        if state in ("MOVE", "RETURN") and self.steps:
            i = min(self.index, len(self.steps) - 1)
            label = _ACTIONS[self.steps[i][0]][2]
            return f"{state}\nSTEP {i + 1}/{len(self.steps)}\n{label}\n{steer}"
        return f"{state}\n\n\n{steer}"


class Mission:
    """State flow of the guide mission: WAIT → MOVE → GUIDE → RETURN → WAIT."""

    def __init__(self, robot: Robot, route, guide_sec: float = 3.0,
                 pause_sec: float = 0.5, return_to_start: bool = True):
        self.robot = robot
        self.route = route                      # Route from the start point to the guide point
        self.guide_sec = guide_sec              # Guiding time (s)
        self.return_to_start = return_to_start  # Whether to come back to the start point after guiding
        self.runner = RouteRunner(robot, pause_sec)
        self.state = "WAIT"                     # Current state: WAIT · MOVE · GUIDE · RETURN
        self.started_at = 0.0                   # Time the mission started
        self.guide_end = 0.0                    # Time to end guiding

    @property
    def running(self) -> bool:
        """True while a mission is running (any state but WAIT)."""
        return self.state != "WAIT"

    def start(self, key: str = "5"):
        """Key 5: starts the mission if the robot is stopped."""
        if self.running:
            log(EVENT, "STATE", f"Key {key} ignored - mission is already running")
            return
        if not self.robot.is_stopped():
            log(EVENT, "STATE", f"Key {key} ignored - wait for READY")
            return
        self.runner.start(self.route, "MOVE")
        if not self.runner.steps:
            log(ALWAYS, "NOTE", "MISSION_ROUTE has no steps - mission not started")
            self.runner.stop()
            return
        self.started_at = _now()
        self.robot.screen_override = lambda: self.runner.screen_text(self.state)
        self._change("MOVE", f"{len(self.runner.steps)} steps")

    def stop(self, key: str = "0"):
        """Key 0: stops the mission and returns to WAIT. Stopping the robot is the caller's job."""
        if not self.running:
            return
        self.runner.stop()
        self.robot.hide_guide()
        self.robot.screen_override = None
        self._change("WAIT", f"stopped (key {key})")

    def update(self):
        """Called on every pass of the main loop. Moves to the next state when the current one is done."""
        now = _now()
        if self.state == "MOVE":                     # MOVE: guide once the route is driven
            if self.runner.done:
                self._change("GUIDE", f"showing guide {self.guide_sec:.1f}s")
                self.robot.show_guide()
                self.guide_end = now + self.guide_sec
        elif self.state == "GUIDE":                  # GUIDE: return once the set time has passed
            if now >= self.guide_end:
                self.robot.hide_guide()
                if self.return_to_start:
                    self._change("RETURN", "same route in reverse")
                    self.runner.start(reverse_route(self.route), "RETURN")
                else:
                    self._finish(now)
        elif self.state == "RETURN":                 # RETURN: mission complete once the route is retraced
            if self.runner.done:
                self._finish(now)
        self.runner.update()

    def _finish(self, now: float):
        self.robot.screen_override = None
        self._change("WAIT", f"mission complete ({now - self.started_at:.1f}s)")

    def _change(self, new_state: str, note: str = ""):
        log(EVENT, "STATE", f"{self.state} → {new_state}" + (f" - {note}" if note else ""))
        self.state = new_state
        self.robot.refresh_screen()
