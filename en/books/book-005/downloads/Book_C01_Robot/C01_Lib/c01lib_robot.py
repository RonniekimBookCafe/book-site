# -*- coding: utf-8 -*-
"""
c01lib_robot.py  |  CORE-01 Educational Library · Robot (the whole robot)
Release 1.6.3

c01lib_app.py uses only this one Robot class.
It never has to touch DCMotor, ServoMotor, LED, or TextScreen directly,
and when you need to, you can open this file and follow where each
command goes.

    Start file (c01_start.py)
      -> c01lib_app.py (reads the keys and calls robot.forward() and so on)
        -> Robot (this file)
          -> DriveMotors / SteeringServos / ScreenFold / InputLED
            -> RoboCo Python API (DCMotor / ServoMotor / LED / TextScreen)
              -> Port
                -> the robot's actual motion
"""

from time import time as _now

from controllables import TextScreen

from . import c01lib_ports as ports
from .c01lib_drive import DriveMotors, MOTOR_SETTINGS, FIXED_SETTINGS, clamp_setting
from .c01lib_steering import SteeringServos
from .c01lib_screen import ScreenFold
from .c01lib_led import InputLED
from .c01lib_log import log, ALWAYS, EVENT, DETAIL


class Robot:
    """Handles the whole CORE-01 Robot 2 (Book-CORE-01-SCRIPT)."""

    # For each action: (key, Text Screen label of 9 characters or fewer, console LOG name)
    _ACTION_INFO = {
        "idle":           ("-", "STOP",     "stop"),
        "forward":        ("W", "FORWARD",  "forward"),
        "backward":       ("S", "BACKWARD", "backward"),
        "turn_left":      ("A", "TURN L",   "turn left"),
        "turn_right":     ("D", "TURN R",   "turn right"),
        "pivot_left":     ("Z", "ROTATE L", "rotate left"),
        "pivot_right":    ("C", "ROTATE R", "rotate right"),
        "diagonal_left":  ("Q", "DIAG L",   "diagonal left"),
        "diagonal_right": ("E", "DIAG R",   "diagonal right"),
    }

    # Steering posture name → console LOG name
    _POSTURE_NAME = {
        "drive": "Drive posture 0°",
        "pivot": "Pivot posture",
        "diag_left": "Diagonal left posture",
        "diag_right": "Diagonal right posture",
    }

    def __init__(self,
                 target_rpm=120.0,
                 acceleration_time=0.5,
                 max_brake_force=50.0,
                 braking_time=0.2,
                 steering_settle_sec: float = 0.5,
                 steering_stagger_sec: float = 0.3,
                 steering_stagger_order: str = "front_rear",
                 stagger_on_release: bool = False,
                 release_return_sec: float = 0.6,
                 text_screen_font_size=None,
                 guide_message: str = "WELCOME"):
        """The arguments mean the same as in the CONTROL PARAMETERS notes in the start file."""
        # Part groups
        self.drive = DriveMotors()
        self.steering = SteeringServos()
        # The screen starts stowed against the body (0°). Right after the robot is loaded
        # the screen servo is already at 0°, so it does not move at startup.
        self.screen = ScreenFold(start_deployed=False)
        self.led = InputLED()
        self.status_screen = TextScreen(ports.PORT_TEXT_SCREEN)

        # Steering order
        self.steering_settle_sec = steering_settle_sec
        self.steering_stagger_sec = steering_stagger_sec
        self.steering_stagger_order = steering_stagger_order
        self.stagger_on_release = stagger_on_release
        self.release_return_sec = release_return_sec

        # Wheel motor baselines, on the same scale as RoboCo's settings panel (DC Motor).
        # They are applied to all four wheels when the script starts; after setup(),
        # motor_settings holds the values actually applied (kept inside the panel's range).
        # A value left as None uses the value from the robot file as is.
        self._motor_config = {"RPM": target_rpm, "ACCEL": acceleration_time,
                              "BRAKE F": max_brake_force, "BRAKE T": braking_time}
        self._motor_file_values = {}     # Robot file values, before the script changed anything
        self._fixed_values = {}          # Values the script does not change (Max Torque)
        self.motor_settings = {}

        # Screen display
        self.text_screen_font_size = text_screen_font_size
        self.guide_message = guide_message

        # State values that change while running
        self._steer_ready_at = 0.0       # The wheels spin only after this time
        self._pending_drive = None       # Wheel drive to run once steering finishes
        self._current_action = None      # Current action ("forward" and so on)
        self._action_started_at = 0.0    # Time the current action started
        self._guide_active = False       # Showing the guide message?
        self._shown_text = None          # Text last written to the Text Screen
        self._shown_steering = False     # Steering state last shown on the screen
        self._screen_dirty = False       # Rewrite the screen on the next update()?

        # Screen to show instead of the status while stopped. None means not used.
        # (Used to show the experiment screen in experiment mode.)
        self.idle_screen = None
        # Screen to show instead of the status at all times. None means not used.
        # (Used to show the mission state during the guide mission.)
        self.screen_override = None

    # ------------------------------------------------------------
    # Startup
    # ------------------------------------------------------------
    def setup(self):
        """Called once when the script starts."""
        self.drive.apply_flip_settings()
        self._apply_motor_settings()
        self.steering.apply_flip_settings()
        self.steering.apply_limits()
        self.screen.apply_limits()
        self.screen.initialize_posture()
        self._initialize_steering()
        self.led.set_color("idle")
        if self.text_screen_font_size is not None:
            self.status_screen.size = self.text_screen_font_size
        self._check_guide_message()
        self._update_status_screen()
        log(ALWAYS, "START", "Ready - wheels 0°, screen folded, motors stopped")

    def _apply_motor_settings(self) -> None:
        """Reads the motor settings from the robot file and applies the baselines to all four wheels.

        A baseline outside the range of RoboCo's settings panel is set to the nearest
        end of the range, with a NOTE in the console (e.g. TARGET_RPM 1200 → 1000).
        The fixed value (Max Torque) is only read and logged.
        """
        for name, (attr, fmt, en, low, high) in MOTOR_SETTINGS.items():
            self._motor_file_values[name] = self.drive.read_setting(attr)[0]
            value = self._motor_config[name]
            if value is None:
                self.motor_settings[name] = self._motor_file_values[name]
                continue
            applied = clamp_setting(name, value)
            if applied != value:
                log(ALWAYS, "NOTE", f"{en} {fmt.format(value)} is outside {fmt.format(low)} - "
                                    f"{fmt.format(high)}; {fmt.format(applied)} is used")
            self.drive.apply_setting(attr, applied)
            self.motor_settings[name] = applied
        for name, (attr, _, _) in FIXED_SETTINGS.items():
            self._fixed_values[name] = self.drive.read_setting(attr)[0]

    def log_settings(self) -> None:
        """Writes this run's settings as SETUP lines (a record of the experiment baseline)."""
        log(ALWAYS, "SETUP", self.settings_summary())

        def motor_line(values):
            return " / ".join(f"{name} {MOTOR_SETTINGS[name][1].format(values[name])}"
                              for name in MOTOR_SETTINGS)
        # The robot file values are the values before the script changed anything. Comparing
        # them with the numbers in RoboCo's settings panel shows whether the units match.
        log(ALWAYS, "SETUP", "Motor (robot file) " + motor_line(self._motor_file_values))
        if self.motor_settings != self._motor_file_values:
            log(ALWAYS, "SETUP", "Motor (script)     " + motor_line(self.motor_settings))
        fixed = " / ".join(f"{name} {FIXED_SETTINGS[name][1].format(self._fixed_values[name])}"
                           for name in FIXED_SETTINGS)
        log(ALWAYS, "SETUP", f"Motor (fixed)      {fixed} - not changed by the script")

    def _initialize_steering(self) -> None:
        """Sets all four wheels to the normal driving posture (0°).

        Unlike a posture change from a key press, there is no stagger and no wait
        before driving. Right after the robot is loaded the wheels are already at 0°,
        so pressing W right away starts the robot immediately.
        """
        now = _now()
        self.steering.begin_posture("drive", now, 0.0)
        self._steer_ready_at = now

    # ------------------------------------------------------------
    # Steering → drive order
    #
    #   Key input
    #     -> _set_posture()   If the wheel posture changes, stop the wheels, start steering,
    #                         and note when steering will finish
    #     -> _request_drive() If steering is done, drive right away;
    #                         if still steering, hold the drive for now
    #     -> update()         Called over and over by the main loop. Advances steering and,
    #                         once steering is done, starts the drive that was held
    #
    # Nothing waits with time.sleep(), so key input keeps being read even while waiting
    # for steering. Releasing the key during the wait means the robot never sets off.
    # ------------------------------------------------------------
    def _set_posture(self, name: str, staggered: bool = True,
                     ramp_sec: float = 0.0) -> None:
        """Requests a wheel steering posture.

        staggered=True : steer two wheels → (steering_stagger_sec) → the other two
        staggered=False: steer all four wheels at once
        ramp_sec > 0   : steer all four wheels together, gradually, over ramp_sec
        """
        now = _now()
        stagger = self.steering_stagger_sec if (staggered and ramp_sec <= 0) else 0.0
        started = self.steering.begin_posture(
            name, now, stagger, self.steering_stagger_order, ramp_sec)
        if started:  # If steering to a new posture has started
            self.drive.stop_all()
            # The wheels spin only after all steering is done and steering_settle_sec has passed.
            self._steer_ready_at = (now + stagger + max(ramp_sec, 0.0)
                                    + self.steering_settle_sec)
            self._screen_dirty = True
            if ramp_sec > 0:
                how = f"slow return {ramp_sec:0.1f}s"
            elif stagger > 0:
                how = ("front → rear stagger" if self.steering_stagger_order == "front_rear"
                       else "diagonal stagger")
            else:
                how = "all four at once"
            log(EVENT, "STEER", f"{self._POSTURE_NAME[name]} ({how})")

    def _request_drive(self, drive_fn) -> None:
        if self._is_steering():
            self._pending_drive = drive_fn
        else:
            self._pending_drive = None
            drive_fn()

    def _is_steering(self) -> bool:
        return _now() < self._steer_ready_at

    def is_steering(self) -> bool:
        """True while the wheels are changing direction (STEERING on the screen)."""
        return self._is_steering()

    def is_stopped(self) -> bool:
        """True when no drive key is held and steering is done (READY on the screen's fourth line)."""
        return (self._current_action or "idle") == "idle" and not self._is_steering()

    def is_driving(self) -> bool:
        """True while a drive key is held and a driving action is running."""
        return (self._current_action or "idle") != "idle"

    def refresh_screen(self) -> None:
        """Asks for the Text Screen to be rewritten on the next update()."""
        self._screen_dirty = True

    def update(self) -> None:
        """Called on every pass of the main loop.

        Advances steering by one step, starts the held wheel drive once steering is
        done, and rewrites the Text Screen if what it should show has changed.
        """
        self.steering.update(_now())
        steering = self._is_steering()
        if self._pending_drive is not None and not steering:
            drive_fn = self._pending_drive
            self._pending_drive = None
            drive_fn()
        # The screen is written at most once per pass, and only when what it should show
        # has changed or the moment STEERING and READY switch.
        if self._screen_dirty or steering != self._shown_steering:
            self._update_status_screen()
            self._screen_dirty = False

    # ------------------------------------------------------------
    # Driving actions (W/S/A/D/Z/C/Q/E)
    # Every action follows the same order: "steering posture → wheel drive."
    # ------------------------------------------------------------
    def forward(self):
        """W key: drives forward with all four wheels at 0°."""
        self._set_posture("drive")
        self._request_drive(lambda: self.drive.all_forward())
        self._on_action_changed("forward")

    def backward(self):
        """S key: drives backward with all four wheels at 0°."""
        self._set_posture("drive")
        self._request_drive(lambda: self.drive.all_backward())
        self._on_action_changed("backward")

    def turn_left(self):
        """A key: leaves the wheels at 0° and spins the left and right sides in opposite directions to turn left."""
        self._set_posture("drive")
        self._request_drive(lambda: self.drive.left_back_right_forward())
        self._on_action_changed("turn_left")

    def turn_right(self):
        """D key: leaves the wheels at 0° and spins the left and right sides in opposite directions to turn right."""
        self._set_posture("drive")
        self._request_drive(lambda: self.drive.left_forward_right_back())
        self._on_action_changed("turn_right")

    def rotate_left(self):
        """Z key: steers the wheels to ±45°, then rotates left in place."""
        self._set_posture("pivot")
        self._request_drive(lambda: self.drive.left_back_right_forward())
        self._on_action_changed("pivot_left")

    def rotate_right(self):
        """C key: steers the wheels to ±45°, then rotates right in place."""
        self._set_posture("pivot")
        self._request_drive(lambda: self.drive.left_forward_right_back())
        self._on_action_changed("pivot_right")

    def diagonal_left(self):
        """Q key: points all four wheels to 10 o'clock, then drives diagonally forward-left."""
        self._set_posture("diag_left")
        self._request_drive(lambda: self.drive.all_forward())
        self._on_action_changed("diagonal_left")

    def diagonal_right(self):
        """E key: points all four wheels to 2 o'clock, then drives diagonally forward-right."""
        self._set_posture("diag_right")
        self._request_drive(lambda: self.drive.all_forward())
        self._on_action_changed("diagonal_right")

    def stop(self):
        """Called when every drive key has been released.

        Stops the wheels and returns them to 0°. All four wheels return together,
        slowly over release_return_sec, so the body does not jolt. Even if W is
        pressed right away, the robot sets off only after the wheels are back at 0°.
        """
        self._pending_drive = None
        self.drive.stop_all()
        self._on_action_changed("idle")  # Log the finished action before the steering LOG
        self._set_posture("drive", staggered=self.stagger_on_release,
                          ramp_sec=self.release_return_sec)

    # ------------------------------------------------------------
    # Opening the screen (experiment keys)
    # ------------------------------------------------------------
    def show_screen(self, reason: str):
        """Opens the screen if it is folded, without showing the guide message.
        If it is already open, leaves it open and only takes down a guide message that was showing.
        reason: reason written to the console (e.g. "key 2 - experiment screen")
        """
        if not self.screen.is_target_deployed():
            self.screen.deploy()
            log(EVENT, "SCREEN", f"Deployed ({reason})")
        self._guide_active = False
        self._screen_dirty = True

    # ------------------------------------------------------------
    # Guide screen (GUIDE state of the guide mission)
    # ------------------------------------------------------------
    def show_guide(self):
        """Opens the screen and shows the guide message (guide_message)."""
        if not self.screen.is_target_deployed():
            self.screen.deploy()
            log(EVENT, "SCREEN", "Deployed (mission) - showing guide message")
        self._guide_active = bool(self.guide_message)
        self._screen_dirty = True

    def hide_guide(self):
        """Ends guiding and folds the screen. Leaves it as is if it is already folded."""
        if self.screen.is_target_deployed():
            self.screen.fold()
            log(EVENT, "SCREEN", "Folded (mission)")
        self._guide_active = False
        self._screen_dirty = True

    # ------------------------------------------------------------
    # Opening and folding the screen (key 1)
    # ------------------------------------------------------------
    def toggle_screen(self):
        """Key 1: opens or folds the screen.

        Opening it while stopped shows the guide message (stop → open the screen →
        guide). Opening it while driving keeps showing the status, because the
        person driving needs to see it.
        """
        self.screen.toggle()
        if self.screen.is_target_deployed():
            stopped = (self._current_action or "idle") == "idle"
            if self.guide_message and stopped:
                self._guide_active = True
                log(EVENT, "SCREEN", "Deployed (key 1) - showing guide message")
            elif self.guide_message:
                log(EVENT, "SCREEN", "Deployed (key 1) - driving, keeping status")
            else:
                log(EVENT, "SCREEN", "Deployed (key 1)")
        else:
            self._guide_active = False
            log(EVENT, "SCREEN", "Folded (key 1)")
        self._screen_dirty = True

    # ------------------------------------------------------------
    # Status display and LOG (only when the state changes)
    # ------------------------------------------------------------
    def _on_action_changed(self, action_key: str):
        if action_key == self._current_action:
            return  # Do nothing while the same action continues
        now = _now()
        previous = self._current_action
        if previous not in (None, "idle"):
            # LOG_LEVEL 2: sum up the finished action in one line.
            key, _, name = self._ACTION_INFO[previous]
            log(DETAIL, "DRIVE", f"{key} {name} | held {now - self._action_started_at:0.2f}s "
                                f"| rpm {self.drive.target_rpm():0.0f}")
        if action_key != "idle" and self._guide_active:
            # Once driving starts, guiding ends and the status shows until the screen is opened again.
            self._guide_active = False
        self._current_action = action_key
        self._action_started_at = now
        self.led.set_color(action_key)
        self._screen_dirty = True

    def _update_status_screen(self):
        """Decides what the Text Screen should show now and writes it.

        [Status] normally
            FORWARD    current action
            KEY W      key the script read
            RPM 120    Target RPM of the wheel motors (0 while steering or stopped)
            READY      steering state (READY / STEERING)

        [Guide message] after key 1 opens the screen while stopped, until a drive key is pressed
            the text in guide_message (e.g. WELCOME)

        [Idle screen] while stopped, when idle_screen is set
            the text idle_screen() returns (e.g. the experiment screen of the experiment script)

        Written within 9 characters per line and 4 lines (c01lib_ports.SCREEN_MAX_*).
        """
        self._shown_steering = self._is_steering()
        action = self._current_action or "idle"
        if self._guide_active:
            text = self.guide_message
        elif self.screen_override is not None:
            text = self.screen_override()
        elif action == "idle" and self.idle_screen is not None:
            text = self.idle_screen()
        else:
            key, label, _ = self._ACTION_INFO[action]
            driving = (action != "idle" and not self._shown_steering
                       and self._pending_drive is None)
            rpm = self.drive.target_rpm() if driving else 0.0
            text = (f"{label}\n"
                    f"KEY {key}\n"
                    f"RPM {rpm:0.0f}\n"
                    f"{'STEERING' if self._shown_steering else 'READY'}")
        self._write_screen(text)

    def _write_screen(self, text: str):
        """Writes to the Text Screen only when the content has changed."""
        if text != self._shown_text:
            self.status_screen.text = text
            self._shown_text = text

    def _check_guide_message(self):
        """Warns in the console when the guide message is longer than the screen and would be cut off."""
        if not self.guide_message:
            return
        lines = self.guide_message.split("\n")
        too_wide = [line for line in lines if len(line) > ports.SCREEN_MAX_CHARS]
        if len(lines) > ports.SCREEN_MAX_LINES or too_wide:
            log(ALWAYS, "NOTE", f"Guide message is longer than the screen ({ports.SCREEN_MAX_CHARS} chars × "
                               f"{ports.SCREEN_MAX_LINES} lines) and may be cut off")

    def show_error(self):
        """Shows on the screen that the script stopped on an error. The caller stops the motors."""
        self._write_screen("ERROR\nSTOPPED\nSEE LOG")

    def settings_summary(self) -> str:
        """Returns the steering settings on one line (logged in the SETUP line at startup)."""
        return (f"Steering wait {self.steering_settle_sec:0.2f}s"
                f" · stagger {self.steering_stagger_sec:0.2f}s · return {self.release_return_sec:0.2f}s")
