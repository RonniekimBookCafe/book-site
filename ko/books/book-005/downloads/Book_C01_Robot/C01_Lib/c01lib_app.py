# -*- coding: utf-8 -*-
"""
c01lib_app.py  |  CORE-01 교육용 라이브러리 · 시작 파일과 로봇 연결
배포 버전 1.6.3

시작 파일(c01_start.py)의 값과 키 배정을 받아 로봇을 준비하고,
메인 루프에서 매번 키를 읽어 세 가지 모드를 움직입니다.

    주행 모드 (PART 1~3)  W·S·A·D·Z·C·Q·E로 주행, 1번으로 화면 펼침·접힘
    실험 모드 (PART 4)    2번을 처음 누르면 시작, 3·4로 값 한 단계씩 변경
    안내 미션 (PART 5)    5번으로 시작, 경로를 스스로 달려 안내하고 복귀

    0번 키는 어느 모드에서나 전체 RESET입니다(헷갈리면 0).
    1번 키로 화면을 접을 때도 0번과 같은 전체 RESET을 합니다.

모드 사이의 규칙
- 안내 미션 중에는 주행 키·1번·2·3·4를 받지 않습니다. 달리는 미션을
  키로 흐트러뜨리지 않기 위해서입니다. 받지 않은 키는 콘솔에 한 줄 남깁니다.
- 5번으로 미션을 시작할 때 실험 모드였다면, 모든 값을 기준값으로 되돌린
  뒤 출발합니다. 미션은 언제나 같은 기준값으로 달립니다.

시작 파일에 적지 않은 값은 아래 DEFAULTS의 값을 씁니다. DEFAULTS에 있는
이름을 시작 파일에 한 줄 적으면 그 값으로 바뀝니다.
    예) LOG_MAX_LINES = 500
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

# 시작 파일에서 바꿀 수 있는 값과 기본값
DEFAULTS = {
    # 바퀴 모터 설정 (RoboCo 설정 창의 DC Motor 값과 같은 기준, None이면 로봇 파일의 값)
    "TARGET_RPM": 120,               # 바퀴 목표 회전수 (0~1000)
    "ACCELERATION_TIME": 0.5,        # 출발할 때 Target RPM까지 걸리는 시간(초, 0~10)
    "MAX_BRAKE_FORCE": 50,           # 멈출 때의 제동력 (0~1570)
    "BRAKING_TIME": 0.2,             # 멈출 때 제동이 걸리는 시간(초, 0~10)
    # 조향
    "STEERING_SETTLE_SEC": 0.5,      # 바퀴 방향을 바꾼 뒤 바퀴를 돌리기까지 기다리는 시간(초)
    "STEERING_STAGGER_SEC": 0.3,     # 앞바퀴를 먼저 돌리고 뒷바퀴를 돌리기까지의 시간(초)
    "STEERING_STAGGER_ORDER": "front_rear",  # "front_rear" 앞 → 뒤 / "diagonal" 대각선끼리
    "STAGGER_ON_RELEASE": False,     # 키를 뗄 때도 시간차 조향을 할지 (RELEASE_RETURN_SEC가 0일 때만)
    "RELEASE_RETURN_SEC": 0.6,       # 키를 뗄 때 바퀴를 0°로 천천히 되돌리는 시간(초)
    "LOOP_DELAY_SEC": 0.02,          # 키 입력을 확인하는 주기(초)
    # 화면과 기록
    "GUIDE_MESSAGE": "WELCOME",      # 안내 문구 (한 줄 9자·4줄 이내)
    "LOG_LEVEL": 1,                  # 콘솔 기록 양 (0·1·2)
    "LOG_MAX_LINES": 200,            # 콘솔 기록 최대 줄 수
    "TEXT_SCREEN_FONT_SIZE": None,   # 로봇 화면 글자 크기 (None이면 로봇 파일의 크기)
    # 키 배정
    "DRIVE_KEYS": {"w": "forward", "s": "backward", "a": "turn_left", "d": "turn_right",
                   "z": "rotate_left", "c": "rotate_right", "q": "diagonal_left", "e": "diagonal_right"},
    "COMMAND_KEYS": {"1": "toggle_screen", "0": "reset", "2": "next_parameter",
                     "3": "level_down", "4": "level_up", "5": "start_mission"},
    # PART 4 실험
    "EXPERIMENT_STEPS": [],
    # PART 5 안내 미션
    "MISSION_ROUTE": [],
    "GUIDE_SEC": 3.0,                # 안내 지점에서 화면을 펼치고 안내하는 시간(초)
    "STEP_PAUSE_SEC": 0.5,           # 동작 하나를 마치고 다음 동작까지 쉬는 시간(초)
    "RETURN_TO_START": True,         # 안내한 뒤 같은 길을 되짚어 출발한 자리로 돌아올지
}

# 1.6.0까지 있던 값. 시작 파일에 남아 있으면 쓰지 않는 이유를 콘솔에 알립니다.
_REMOVED = {
    "MOTOR_POWER_RATIO": "wheel speed is set by TARGET_RPM",
    "TURN_POWER_RATIO": "wheel speed is set by TARGET_RPM",
    "PIVOT_POWER_RATIO": "wheel speed is set by TARGET_RPM",
    "MAX_TORQUE": "Max Torque is fixed in the robot file",
}

# 키 배정에 쓸 수 있는 동작과 콘솔에 보여 줄 짧은 이름
_DRIVE_ACTIONS = {"forward": "forward", "backward": "back", "turn_left": "turn left",
                  "turn_right": "turn right", "rotate_left": "rotate left",
                  "rotate_right": "rotate right", "diagonal_left": "diag left",
                  "diagonal_right": "diag right"}
_COMMANDS = ("toggle_screen", "reset", "next_parameter", "level_down", "level_up", "start_mission")


class RobotApp:
    """시작 파일의 값으로 로봇을 준비하고, 메인 루프를 한 번씩 진행하는 클래스."""

    def __init__(self, script_values: dict):
        """script_values: 시작 파일의 globals(). 대문자 이름의 값만 읽습니다."""
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

        # 스크립트를 멈출 때도 마무리 코드(shutdown)가 실행되도록 RoboCo에 요청합니다.
        Runtime.require_force_close()

    # ------------------------------------------------------------
    # 준비: 키 배정 확인
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
    # 반복: 메인 루프
    # ------------------------------------------------------------
    def running(self) -> bool:
        """스크립트를 멈추기 전까지 True."""
        return not Runtime.quitting()

    def update(self):
        """메인 루프에서 매번 부릅니다. 키를 읽고, 로봇·실험·미션을 한 단계 진행합니다."""
        try:
            self._update()
            sleep(self.loop_delay)
        except Exception as error:
            # 오류가 나도 값을 기준값으로 되돌리고 모터를 멈춘 뒤, LOG와 화면에 남깁니다.
            self.mission.runner.stop()
            self.experiment.restore_all()
            self.robot.stop()
            self.robot.show_error()
            log(ALWAYS, "ERROR", f"{type(error).__name__}: {error} - motors stopped, script halted")
            raise  # Python 오류 메시지(Traceback)도 그대로 보여 줌

    def _update(self):
        mission = self.mission.running

        # 0: 전체 RESET (어느 모드에서나)
        if self._pressed("reset"):
            key = self.command_keys["reset"][0]
            self.mission.stop(key)
            self.experiment.reset(f"key {key}")
            self.drive_keys.clear()      # 누르고 있던 주행 키는 뗐다가 다시 눌러야 움직임
            mission = False

        # 2·3·4: PART 4 실험 키
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

        # 5: PART 5 안내 미션 시작
        if self._pressed("start_mission"):
            key = self.command_keys["start_mission"][0]
            if not self.mission.running and self.robot.is_stopped():
                self.experiment.end_for_mission()
            self.mission.start(key)
            mission = self.mission.running

        # 주행 키 (미션 중에는 받지 않음)
        self.drive_keys.update(self.robot.stop, blocked=self._blocked if mission else None)

        # 1: 화면 펼침·접힘 (미션 중에는 받지 않음). 접을 때는 0번과 같은 전체 RESET
        if self._pressed("toggle_screen"):
            key = self.command_keys["toggle_screen"][0]
            if mission:
                self._blocked(key)
            else:
                self.robot.toggle_screen()
                if not self.robot.screen.is_target_deployed():   # 방금 접었다면
                    self.experiment.reset(f"key {key} - screen folded")
                    self.drive_keys.clear()  # 누르고 있던 주행 키는 뗐다가 다시 눌러야 움직임

        self.mission.update()
        self.robot.update()

    def _pressed(self, name: str) -> bool:
        return name in self.command_keys and pressed(self.command_keys[name][1])

    def _blocked(self, key: str):
        log(EVENT, "STATE", f"Key {key.upper()} ignored - mission is running")

    # ------------------------------------------------------------
    # 마무리
    # ------------------------------------------------------------
    def shutdown(self):
        """스크립트를 멈출 때 부릅니다. 값을 기준값으로 되돌리고 모터를 멈춥니다."""
        if self.mission.running:
            self.mission.runner.stop()
            self.robot.hide_guide()
        self.experiment.restore_all()
        self.robot.stop()
        log(ALWAYS, "END", "Script stopped - motors off, settings restored")
