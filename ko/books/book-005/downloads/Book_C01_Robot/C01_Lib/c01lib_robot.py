# -*- coding: utf-8 -*-
"""
c01lib_robot.py  |  CORE-01 교육용 라이브러리 · Robot (로봇 전체)
배포 버전 1.6.3

c01lib_app.py는 이 Robot 클래스 하나만
가져다 씁니다. DCMotor·ServoMotor·LED·TextScreen을 직접 다루지 않아도
되고, 필요할 때는 이 파일을 열어 명령이 어디로 이어지는지 따라갈 수
있습니다.

    시작 파일 (c01_start.py)
      -> c01lib_app.py (키를 읽고 robot.forward() 등을 부름)
        -> Robot (이 파일)
          -> DriveMotors / SteeringServos / ScreenFold / InputLED
            -> RoboCo Python API (DCMotor / ServoMotor / LED / TextScreen)
              -> Port
                -> 로봇의 실제 움직임
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
    """CORE-01 로봇2(Book-CORE-01-SCRIPT) 전체를 다루는 클래스."""

    # 동작별 (키, Text Screen 표시 9자 이내, 콘솔 LOG 이름)
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

    # 조향 자세 이름 → 콘솔 LOG 이름
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
        """인자의 뜻은 시작 파일의 CONTROL PARAMETERS 설명과 같습니다."""
        # 부품 묶음
        self.drive = DriveMotors()
        self.steering = SteeringServos()
        # 화면은 차체에 붙은 수납 상태(0°)로 시작합니다. 로봇을 불러온 직후
        # 화면 서보는 이미 0°이므로 시작할 때 움직이지 않습니다.
        self.screen = ScreenFold(start_deployed=False)
        self.led = InputLED()
        self.status_screen = TextScreen(ports.PORT_TEXT_SCREEN)

        # 조향 순서
        self.steering_settle_sec = steering_settle_sec
        self.steering_stagger_sec = steering_stagger_sec
        self.steering_stagger_order = steering_stagger_order
        self.stagger_on_release = stagger_on_release
        self.release_return_sec = release_return_sec

        # 바퀴 모터 설정 기준값. RoboCo 설정 창(DC Motor)의 값과 같은 기준입니다.
        # 스크립트를 시작할 때 네 바퀴에 적용하고, setup() 뒤에는 motor_settings에
        # 실제로 적용한 값(설정 창의 범위에 맞춘 값)이 들어갑니다.
        # None으로 두면 그 값은 로봇 파일의 값을 그대로 씁니다.
        self._motor_config = {"RPM": target_rpm, "ACCEL": acceleration_time,
                              "BRAKE F": max_brake_force, "BRAKE T": braking_time}
        self._motor_file_values = {}     # 스크립트가 바꾸기 전 로봇 파일의 값
        self._fixed_values = {}          # 스크립트가 바꾸지 않는 값 (Max Torque)
        self.motor_settings = {}

        # 화면 표시
        self.text_screen_font_size = text_screen_font_size
        self.guide_message = guide_message

        # 실행 중에 바뀌는 상태 값
        self._steer_ready_at = 0.0       # 이 시각이 지나야 바퀴를 돌림
        self._pending_drive = None       # 조향이 끝나면 실행할 바퀴 구동
        self._current_action = None      # 지금 동작 ("forward" 등)
        self._action_started_at = 0.0    # 지금 동작을 시작한 시각
        self._guide_active = False       # 안내 문구를 보여 주는 중인가
        self._shown_text = None          # Text Screen에 마지막으로 쓴 글
        self._shown_steering = False     # 화면에 마지막으로 표시한 조향 상태
        self._screen_dirty = False       # 다음 update()에서 화면을 다시 쓸지

        # 멈춰 있을 때 상태 정보 대신 보여 줄 화면. None이면 쓰지 않습니다.
        # (실험 모드에서 실험 화면을 보여 줄 때 씁니다.)
        self.idle_screen = None
        # 언제나 상태 정보 대신 보여 줄 화면. None이면 쓰지 않습니다.
        # (안내 미션에서 미션 상태를 보여 줄 때 씁니다.)
        self.screen_override = None

    # ------------------------------------------------------------
    # 시작 준비
    # ------------------------------------------------------------
    def setup(self):
        """스크립트를 시작할 때 한 번 호출합니다."""
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
        """로봇 파일의 모터 설정 값을 읽어 두고, 기준값을 네 바퀴에 적용합니다.

        기준값이 RoboCo 설정 창의 범위를 벗어나면 범위 끝 값으로 맞추고 콘솔에
        NOTE를 남깁니다(예: TARGET_RPM 1200 → 1000). 고정값(Max Torque)은
        읽어서 기록만 합니다.
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
        """이번 실행의 설정값을 SETUP 줄로 남깁니다(실험 기준 조건 기록)."""
        log(ALWAYS, "SETUP", self.settings_summary())

        def motor_line(values):
            return " / ".join(f"{name} {MOTOR_SETTINGS[name][1].format(values[name])}"
                              for name in MOTOR_SETTINGS)
        # 로봇 파일 값은 스크립트가 바꾸기 전의 값입니다. RoboCo 설정 창의
        # 숫자와 비교하면 단위가 같은지 확인할 수 있습니다.
        log(ALWAYS, "SETUP", "Motor (robot file) " + motor_line(self._motor_file_values))
        if self.motor_settings != self._motor_file_values:
            log(ALWAYS, "SETUP", "Motor (script)     " + motor_line(self.motor_settings))
        fixed = " / ".join(f"{name} {FIXED_SETTINGS[name][1].format(self._fixed_values[name])}"
                           for name in FIXED_SETTINGS)
        log(ALWAYS, "SETUP", f"Motor (fixed)      {fixed} - not changed by the script")

    def _initialize_steering(self) -> None:
        """네 바퀴를 기본 주행 자세(0°)로 맞춥니다.

        키를 눌러 자세를 바꿀 때와 달리 시간차도, 구동 대기 시간도 두지
        않습니다. 로봇을 불러온 직후 바퀴는 이미 0°이므로, 시작하자마자
        W를 눌러도 바로 출발하게 하기 위해서입니다.
        """
        now = _now()
        self.steering.begin_posture("drive", now, 0.0)
        self._steer_ready_at = now

    # ------------------------------------------------------------
    # 조향 → 구동 순서
    #
    #   키 입력
    #     -> _set_posture()   바퀴 자세가 바뀌면 바퀴를 멈추고 조향 시작,
    #                         조향이 끝날 시각을 기록
    #     -> _request_drive() 조향이 끝났으면 바로 구동,
    #                         조향 중이면 구동을 잠시 보류
    #     -> update()         메인 루프가 반복해서 부름. 조향을 진행하고,
    #                         조향이 끝나면 보류한 구동을 시작
    #
    # time.sleep()으로 멈춰 기다리지 않으므로, 조향을 기다리는 동안에도
    # 키 입력을 계속 읽습니다. 기다리는 중에 키를 떼면 출발하지 않습니다.
    # ------------------------------------------------------------
    def _set_posture(self, name: str, staggered: bool = True,
                     ramp_sec: float = 0.0) -> None:
        """바퀴 조향 자세를 요청합니다.

        staggered=True : 두 바퀴 조향 → (steering_stagger_sec) → 나머지 두 바퀴
        staggered=False: 네 바퀴 동시 조향
        ramp_sec > 0   : 네 바퀴를 함께 ramp_sec 동안 천천히 조향
        """
        now = _now()
        stagger = self.steering_stagger_sec if (staggered and ramp_sec <= 0) else 0.0
        started = self.steering.begin_posture(
            name, now, stagger, self.steering_stagger_order, ramp_sec)
        if started:  # 새 자세로 조향을 시작했다면
            self.drive.stop_all()
            # 조향이 모두 끝나고 steering_settle_sec가 지나야 바퀴를 돌립니다.
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
        """바퀴 방향을 바꾸는 중이면 True (화면의 STEERING)."""
        return self._is_steering()

    def is_stopped(self) -> bool:
        """주행 키를 누르지 않았고 조향도 끝난 상태(화면 넷째 줄 READY)면 True."""
        return (self._current_action or "idle") == "idle" and not self._is_steering()

    def is_driving(self) -> bool:
        """주행 키를 누르고 있어 주행 동작 중이면 True."""
        return (self._current_action or "idle") != "idle"

    def refresh_screen(self) -> None:
        """다음 update()에서 Text Screen을 다시 쓰도록 요청합니다."""
        self._screen_dirty = True

    def update(self) -> None:
        """메인 루프에서 매 반복마다 호출합니다.

        조향을 한 단계 진행하고, 조향이 끝났으면 보류한 바퀴 구동을
        시작하고, 표시할 내용이 바뀌었으면 Text Screen을 다시 씁니다.
        """
        self.steering.update(_now())
        steering = self._is_steering()
        if self._pending_drive is not None and not steering:
            drive_fn = self._pending_drive
            self._pending_drive = None
            drive_fn()
        # 화면은 한 번 반복할 때 한 번만 씁니다. 표시할 내용이 바뀌었거나
        # STEERING과 READY가 바뀐 순간에만 다시 씁니다.
        if self._screen_dirty or steering != self._shown_steering:
            self._update_status_screen()
            self._screen_dirty = False

    # ------------------------------------------------------------
    # 주행 동작 (W·S·A·D·Z·C·Q·E)
    # 모든 동작이 "조향 자세 → 바퀴 구동" 순서를 똑같이 따릅니다.
    # ------------------------------------------------------------
    def forward(self):
        """W 키: 네 바퀴 0°에서 전진합니다."""
        self._set_posture("drive")
        self._request_drive(lambda: self.drive.all_forward())
        self._on_action_changed("forward")

    def backward(self):
        """S 키: 네 바퀴 0°에서 후진합니다."""
        self._set_posture("drive")
        self._request_drive(lambda: self.drive.all_backward())
        self._on_action_changed("backward")

    def turn_left(self):
        """A 키: 바퀴는 0° 그대로 두고 좌우 바퀴를 반대로 돌려 왼쪽으로 돕니다."""
        self._set_posture("drive")
        self._request_drive(lambda: self.drive.left_back_right_forward())
        self._on_action_changed("turn_left")

    def turn_right(self):
        """D 키: 바퀴는 0° 그대로 두고 좌우 바퀴를 반대로 돌려 오른쪽으로 돕니다."""
        self._set_posture("drive")
        self._request_drive(lambda: self.drive.left_forward_right_back())
        self._on_action_changed("turn_right")

    def rotate_left(self):
        """Z 키: 바퀴를 ±45°로 조향한 뒤 제자리에서 좌회전합니다."""
        self._set_posture("pivot")
        self._request_drive(lambda: self.drive.left_back_right_forward())
        self._on_action_changed("pivot_left")

    def rotate_right(self):
        """C 키: 바퀴를 ±45°로 조향한 뒤 제자리에서 우회전합니다."""
        self._set_posture("pivot")
        self._request_drive(lambda: self.drive.left_forward_right_back())
        self._on_action_changed("pivot_right")

    def diagonal_left(self):
        """Q 키: 네 바퀴를 10시 방향으로 맞춘 뒤 왼쪽 대각선으로 전진합니다."""
        self._set_posture("diag_left")
        self._request_drive(lambda: self.drive.all_forward())
        self._on_action_changed("diagonal_left")

    def diagonal_right(self):
        """E 키: 네 바퀴를 2시 방향으로 맞춘 뒤 오른쪽 대각선으로 전진합니다."""
        self._set_posture("diag_right")
        self._request_drive(lambda: self.drive.all_forward())
        self._on_action_changed("diagonal_right")

    def stop(self):
        """주행 키를 모두 떼었을 때 호출합니다.

        바퀴를 멈추고, 바퀴를 0°로 되돌립니다. 되돌릴 때는 네 바퀴를 함께,
        release_return_sec 동안 천천히 돌려 차체가 들썩이지 않게 합니다.
        바로 W를 눌러도 바퀴가 0°로 돌아온 뒤에 출발합니다.
        """
        self._pending_drive = None
        self.drive.stop_all()
        self._on_action_changed("idle")  # 끝난 동작의 LOG를 조향 LOG보다 먼저 남김
        self._set_posture("drive", staggered=self.stagger_on_release,
                          ramp_sec=self.release_return_sec)

    # ------------------------------------------------------------
    # 화면 펼치기 (실험 키)
    # ------------------------------------------------------------
    def show_screen(self, reason: str):
        """화면이 접혀 있으면 펼칩니다. 안내 문구는 띄우지 않습니다.
        이미 펼쳐져 있으면 그대로 두고, 보이던 안내 문구만 내립니다.
        reason: 콘솔에 남길 이유 (예: "key 2 - experiment screen")
        """
        if not self.screen.is_target_deployed():
            self.screen.deploy()
            log(EVENT, "SCREEN", f"Deployed ({reason})")
        self._guide_active = False
        self._screen_dirty = True

    # ------------------------------------------------------------
    # 안내 화면 (안내 미션의 GUIDE 상태)
    # ------------------------------------------------------------
    def show_guide(self):
        """화면을 펼치고 안내 문구(guide_message)를 보여 줍니다."""
        if not self.screen.is_target_deployed():
            self.screen.deploy()
            log(EVENT, "SCREEN", "Deployed (mission) - showing guide message")
        self._guide_active = bool(self.guide_message)
        self._screen_dirty = True

    def hide_guide(self):
        """안내를 끝내고 화면을 접습니다. 이미 접혀 있으면 그대로 둡니다."""
        if self.screen.is_target_deployed():
            self.screen.fold()
            log(EVENT, "SCREEN", "Folded (mission)")
        self._guide_active = False
        self._screen_dirty = True

    # ------------------------------------------------------------
    # 화면 펼침·접힘 (1번 키)
    # ------------------------------------------------------------
    def toggle_screen(self):
        """1번 키: 화면을 펼치거나 접습니다.

        멈춘 상태에서 펼치면 안내 문구를 보여 줍니다(정지 → 화면 펼침 →
        안내 순서). 주행 중에 펼치면 조종하는 사람이 상태를 봐야 하므로
        상태 정보를 그대로 보여 줍니다.
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
    # 상태 표시와 LOG (상태가 바뀔 때만)
    # ------------------------------------------------------------
    def _on_action_changed(self, action_key: str):
        if action_key == self._current_action:
            return  # 같은 동작이 이어지는 중이면 아무것도 하지 않음
        now = _now()
        previous = self._current_action
        if previous not in (None, "idle"):
            # LOG_LEVEL 2: 끝난 동작을 한 줄로 요약합니다.
            key, _, name = self._ACTION_INFO[previous]
            log(DETAIL, "DRIVE", f"{key} {name} | held {now - self._action_started_at:0.2f}s "
                                f"| rpm {self.drive.target_rpm():0.0f}")
        if action_key != "idle" and self._guide_active:
            # 주행을 시작하면 안내를 끝내고, 다시 펼칠 때까지 상태 정보를 보여 줍니다.
            self._guide_active = False
        self._current_action = action_key
        self._action_started_at = now
        self.led.set_color(action_key)
        self._screen_dirty = True

    def _update_status_screen(self):
        """Text Screen에 지금 보여 줄 내용을 정해 씁니다.

        [상태 정보] 평소
            FORWARD    지금 동작
            KEY W      스크립트가 읽은 키
            RPM 120    바퀴 모터의 Target RPM (조향 중·정지 중에는 0)
            READY      조향 상태 (READY / STEERING)

        [안내 문구] 멈춘 상태에서 1번 키로 화면을 펼친 뒤, 주행 키를 누르기 전까지
            guide_message의 글 (예: WELCOME)

        [멈춤 화면] 멈춰 있고 idle_screen이 정해져 있을 때
            idle_screen()이 돌려주는 글 (예: 실험 스크립트의 실험 화면)

        한 줄 9자, 4줄 이내(c01lib_ports.SCREEN_MAX_*)로 씁니다.
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
        """내용이 바뀌었을 때만 Text Screen에 씁니다."""
        if text != self._shown_text:
            self.status_screen.text = text
            self._shown_text = text

    def _check_guide_message(self):
        """안내 문구가 화면보다 길면 잘려 보이므로 콘솔에 알립니다."""
        if not self.guide_message:
            return
        lines = self.guide_message.split("\n")
        too_wide = [line for line in lines if len(line) > ports.SCREEN_MAX_CHARS]
        if len(lines) > ports.SCREEN_MAX_LINES or too_wide:
            log(ALWAYS, "NOTE", f"Guide message is longer than the screen ({ports.SCREEN_MAX_CHARS} chars × "
                               f"{ports.SCREEN_MAX_LINES} lines) and may be cut off")

    def show_error(self):
        """오류로 스크립트가 멈출 때 화면에 알립니다. 모터는 호출하는 쪽에서 멈춥니다."""
        self._write_screen("ERROR\nSTOPPED\nSEE LOG")

    def settings_summary(self) -> str:
        """조향 설정값을 한 줄로 돌려줍니다(시작할 때 SETUP 줄에 기록)."""
        return (f"Steering wait {self.steering_settle_sec:0.2f}s"
                f" · stagger {self.steering_stagger_sec:0.2f}s · return {self.release_return_sec:0.2f}s")
