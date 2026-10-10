# -*- coding: utf-8 -*-
"""
c01lib_experiment.py  |  CORE-01 교육용 라이브러리 · 실험 키 (2·3·4·0, 1번 접기)
배포 버전 1.6.3

시작 파일의 EXPERIMENT_STEPS(실험 단계표)를 받아, 주행 키로 로봇을
움직이면서 숫자 키로 바퀴 모터 설정 값을 바꿔 볼 수 있게 합니다. 키는
c01lib_app.py가 읽어서 이 파일의 함수(select_next, step, reset)를 부릅니다.

    2  실험 모드 시작 / 다음 값 고르기 (RPM → ACCEL → BRAKE F → BRAKE T → 다시 RPM)
    3  고른 값을 한 단계 낮춤  (Level Down)
    4  고른 값을 한 단계 높임  (Level Up)
    0  전체 RESET (Reset All). 헷갈리면 0
    1  화면을 접으면 0과 같은 전체 RESET

규칙
- 실험 모드는 2번을 처음 누를 때 시작합니다. 그 전까지 로봇 화면과 LOG는
  평소와 같고, 3·4를 누르면 값을 바꾸지 않고 "먼저 2를 누르라"고 남깁니다.
- 2·3·4는 멈춘 상태에서만 받습니다. 멈춘 상태는 주행 키를 누르지 않았고
  화면 넷째 줄이 READY인 때입니다. 달리는 도중에 값이 바뀌지 않게 합니다.
- 2·3·4를 받으면 화면이 접혀 있을 때 저절로 펼칩니다. 실험 결과는 로봇
  화면에 나타나기 때문입니다.
- 3·4로 바꾼 값은 2번으로 다른 값을 골라도 그대로 유지됩니다. 여러 값을
  함께 바꿔 둔 채 주행할 수 있습니다.
- 0을 누르거나 1번으로 화면을 접으면 3·4로 바꾼 값이 모두 기준값으로
  돌아가고, 바퀴를 멈추고, 바퀴 방향을 0°로 되돌리고, 실험 모드를 끝냅니다.
  그때 누르고 있던 주행 키는 한 번 뗐다가 다시 눌러야 움직입니다.

단계표에는 값마다 LV 1 ~ LV n(기본 10단계)의 값을 작은 값부터 적습니다.
기준값은 시작 파일의 CONTROL PARAMETERS 값이고, 기준값과 같은 단계가
기본 단계입니다.
- 단계표에 기준값과 같은 값이 없으면 가장 가까운 단계를 기준값으로 바꾸고
  콘솔에 NOTE를 남깁니다. 기준값은 CONTROL PARAMETERS 한 곳에만 둡니다.
- 모터 설정 값의 단계가 RoboCo 설정 창의 범위(예: Target RPM 0~1000)를
  넘으면 범위 끝 값으로 맞추고 콘솔에 NOTE를 남깁니다.

사용하는 RoboCo 공식 API
- DCMotor.max_rpm, acceleration_time, brake_force, brake_time
  (값을 넣는 순간 모터에 적용)
"""

from .c01lib_drive import MOTOR_SETTINGS, clamp_setting
from .c01lib_log import log, ALWAYS, EVENT
from .c01lib_robot import Robot

# 실험 항목: 화면 이름 → (LOG 이름, 화면 값 형식, 바꾸는 곳, 바꾸는 값 이름)
#   바꾸는 곳 "motor": 네 바퀴 DC Motor의 설정 값 (기본 단계표에 있는 네 가지)
#   바꾸는 곳 "robot": Robot의 조향 설정 값 (단계표에 줄을 더하면 쓸 수 있음)
_ITEMS = {name: (en, fmt, "motor", attr) for name, (attr, fmt, en, _, _) in MOTOR_SETTINGS.items()}
_ITEMS.update({
    "STAGGER": ("Stagger",       "{:.2f} s", "robot", "steering_stagger_sec"),
    "RETURN":  ("Return time",   "{:.2f} s", "robot", "release_return_sec"),
})

# 1.6.0까지 있던 실험 항목. 단계표에 남아 있으면 쓰지 않는 이유를 콘솔에 알립니다.
_REMOVED_ITEMS = {
    "POWER": "wheel speed is set by RPM",
    "TORQUE": "Max Torque is fixed in the robot file",
}


def _same(a: float, b: float) -> bool:
    """두 값이 같은 값인가 (소수 계산의 아주 작은 오차는 같은 것으로 봄)."""
    return abs(a - b) < 1e-6


class _Item:
    """단계표의 한 줄(실험할 값 하나)."""

    def __init__(self, name, base, values):
        self.name = name
        self.log_name, self.fmt, self.target, self.attr = _ITEMS[name]
        steps = [float(v) for v in values]                 # LV 1 ~ LV n 의 값
        self.clamped = False                               # 범위에 맞춰 바꾼 단계가 있는가
        if self.target == "motor":                         # RoboCo 설정 창의 범위 안으로
            limited = [clamp_setting(name, v) for v in steps]
            self.clamped = limited != steps
            steps = limited
        self.base_replaced = not any(_same(v, base) for v in steps)
        if self.base_replaced:                             # 기준값이 없으면 가장 가까운 단계를 기준값으로
            nearest = min(range(len(steps)), key=lambda i: abs(steps[i] - base))
            steps[nearest] = base
        self.steps = sorted(set(steps))                    # 작은 값부터, 같은 값은 하나만
        self.base_level = next(i for i, v in enumerate(self.steps) if _same(v, base))
        self.level = self.base_level

    @property
    def value(self):
        return self.steps[self.level]

    @property
    def changed(self) -> bool:
        """3·4로 바꿔 기준값과 다른 단계에 있으면 True."""
        return self.level != self.base_level

    def text(self, value):
        return self.fmt.format(value)

    def lv(self):
        return f"LV {self.level + 1}/{len(self.steps)}"


class Experiment:
    """실험 단계표를 들고 실험 키(2·3·4·0, 1번 접기)를 처리하는 클래스."""

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
        self.active = False       # 실험 모드인가 (2번을 처음 누르면 시작)
        self.just_reset = False   # RESET 직후 화면에 RESET을 보여 주는 중인가
        self.selected = 0

    # ------------------------------------------------------------
    # 메인 루프에서 매 반복마다 부름
    # ------------------------------------------------------------
    def update(self):
        """RESET 뒤 다시 주행을 시작하면 화면의 RESET 표시를 지웁니다."""
        if self.just_reset and self.robot.is_driving():
            self.just_reset = False
            self._show(None)

    # ------------------------------------------------------------
    # 실험 키
    # ------------------------------------------------------------
    def _stopped(self, key: str) -> bool:
        if self.robot.is_stopped():
            return True
        log(EVENT, "EXP", f"Key {key} ignored - release drive keys and wait for READY")
        return False

    def select_next(self, key: str = "2"):
        """2번 키: 실험 모드를 시작하거나, 다음 값을 고릅니다.
        앞에서 3·4로 바꾼 값은 그대로 둡니다.
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
        """3번 키(delta=-1), 4번 키(delta=+1): 고른 값을 한 단계 바꿉니다."""
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
        """0번 키, 또는 1번 키로 화면을 접을 때: 전체 RESET. 언제든 동작합니다.

        3·4로 바꾼 값을 모두 기준값으로 되돌리고, 바퀴를 멈추고, 바퀴 방향을
        0°로 되돌리고, 실험 모드를 끝냅니다.
        reason: 콘솔에 남길 이유 (예: "key 0", "key 1 - screen folded")
        """
        self.restore_all()
        self.active = False
        self.selected = 0
        self.just_reset = True
        log(ALWAYS, "EXP", f"RESET ({reason}) - all values to base, wheels stopped and back to 0°. "
                           "Release drive keys, then press again")
        self.robot.stop()        # 바퀴 정지 + 바퀴 방향 0°로 천천히 복귀
        self._show(self.screen_text)

    def end_for_mission(self):
        """미션을 시작하기 전에 실험 모드를 끝내고 모든 값을 기준값으로 되돌립니다.
        미션은 언제나 같은 기준값으로 달리게 하기 위해서입니다.
        """
        changed = self.active or any(item.changed for item in self.items)
        self.restore_all()
        self.active = False
        self.just_reset = False
        self._show(None)
        if changed:
            log(EVENT, "EXP", "Experiment mode off - all values back to base for the mission")

    def restore_all(self):
        """모든 값을 기준값으로 되돌립니다(RESET, 화면 접기, 미션 시작, 스크립트 종료)."""
        for item in self.items:
            item.level = item.base_level
            self._apply(item)

    def _apply(self, item: _Item):
        """값을 로봇에 바로 적용합니다."""
        if item.target == "motor":
            self.robot.drive.apply_setting(item.attr, item.value)
        else:
            setattr(self.robot, item.attr, item.value)

    # ------------------------------------------------------------
    # 멈춰 있을 때의 화면
    # ------------------------------------------------------------
    def _show(self, screen_fn):
        self.robot.idle_screen = screen_fn
        self.robot.refresh_screen()

    def screen_text(self) -> str:
        """멈춰 있을 때의 Text Screen 4줄 (한 줄 9자 이내).

            실험 모드              RESET 직후
            RPM       고른 값      RESET
            LV 4/10   지금 단계    KEY 0
            120 rpm   지금 값      RPM 0
            READY     조향 상태    READY (또는 STEERING)
        """
        state = "STEERING" if self.robot.is_steering() else "READY"
        if self.just_reset:
            return f"RESET\nKEY 0\nRPM 0\n{state}"
        item = self.items[self.selected]
        return f"{item.name}\n{item.lv()}\n{item.text(item.value)}\n{state}"
