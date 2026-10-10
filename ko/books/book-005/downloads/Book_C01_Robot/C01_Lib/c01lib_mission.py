# -*- coding: utf-8 -*-
"""
c01lib_mission.py  |  CORE-01 교육용 라이브러리 · 안내 미션 경로
배포 버전 1.6.3

안내 미션을 실행합니다. 시작 파일의 5번 키로 시작하고, 0번 키로 언제든
멈춥니다. 미션은 네 가지 상태를 차례로 지나갑니다.

    WAIT(대기) → MOVE(이동) → GUIDE(안내) → RETURN(복귀) → WAIT

- Mission     : 상태 흐름 (지금 상태에서 다음 상태로 넘어가는 규칙)
- RouteRunner : MOVE와 RETURN에서 경로의 동작을 하나씩 실행

경로(MISSION_ROUTE)는 로봇이 서 있는 자리를 기준으로 한 동작과 시간의
목록입니다.

    MISSION_ROUTE = [("forward", 2.0), ("rotate_right", 0.5), ("forward", 1.5)]

동작 하나는 다음 순서로 실행됩니다.

    동작 시작 → (바퀴 방향을 바꿔야 하면 조향이 끝날 때까지 기다림)
    → 정한 시간 동안 주행 → 정지 → 멈출 때까지 기다림 → 잠깐 쉼 → 다음 동작

주행 시간은 바퀴가 실제로 구르기 시작한 때부터 잽니다. 이 로봇에는
위치를 재는 센서가 없으므로, 동작이 끝났다는 것은 "정한 시간만큼
움직였다"는 뜻이지 "목표 지점에 도착했다"는 뜻은 아닙니다.

time.sleep()으로 멈춰 기다리지 않으므로, 미션이 진행되는 동안에도
0번 키(미션 중단)를 계속 읽을 수 있습니다.
"""

from time import time as _now

from .c01lib_log import log, ALWAYS, EVENT
from .c01lib_robot import Robot

# 경로에 쓸 수 있는 동작: 이름 → (Robot 동작, 되돌아갈 때의 동작, 화면 표시, LOG 이름)
# pause는 움직이지 않고 정한 시간만큼 기다립니다.
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
    """같은 길을 거꾸로 되짚는 경로를 만듭니다.
    순서를 뒤집고, 각 동작을 반대 동작으로 바꿉니다(앞으로 ↔ 뒤로,
    왼쪽 ↔ 오른쪽). 차체 방향은 바꾸지 않고 뒤로 되돌아옵니다.
    """
    return [(_ACTIONS[action][1], sec) for action, sec in reversed(route) if action in _ACTIONS]


def describe_route(route) -> str:
    """경로를 한 줄로 적습니다. 예: forward 2.0s → rotate right 0.5s"""
    return " → ".join(f"{_ACTIONS[a][3]} {sec:.1f}s" for a, sec in route if a in _ACTIONS)


class RouteRunner:
    """경로의 동작을 하나씩 차례로 실행하는 클래스."""

    def __init__(self, robot: Robot, pause_sec: float = 0.5):
        self.robot = robot
        self.pause_sec = pause_sec      # 동작 하나를 마치고 다음 동작까지 쉬는 시간
        self.steps = []
        self.index = 0
        self.label = ""                 # 지금 실행 중인 상태 이름 (MOVE / RETURN)
        self.phase = "idle"             # idle · begin · steer · drive · settle · pause · done
        self.phase_end = 0.0

    def start(self, route, label: str):
        """경로 실행을 시작합니다. 쓸 수 없는 동작은 건너뜁니다."""
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
        """경로 실행을 멈춥니다. 로봇을 멈추는 일은 호출하는 쪽에서 합니다."""
        self.steps = []
        self.phase = "idle"

    @property
    def done(self) -> bool:
        """경로의 모든 동작을 마쳤으면 True."""
        return self.phase == "done"

    def update(self):
        """메인 루프에서 매 반복마다 호출합니다. 지금 동작을 한 단계 진행합니다."""
        now = _now()
        if self.phase == "begin":
            if self.index >= len(self.steps):
                self.phase = "done"
                return
            action, sec = self.steps[self.index]
            method, _, _, name = _ACTIONS[action]
            log(EVENT, "STATE", f"{self.label} step {self.index + 1}/{len(self.steps)}: {name} {sec:.2f}s")
            if method is None:                      # pause: 움직이지 않고 기다림
                self.phase, self.phase_end = "pause", now + sec
            else:
                getattr(self.robot, method)()       # 필요하면 조향부터 시작됨
                self.phase = "steer"
            self.robot.refresh_screen()
        elif self.phase == "steer":
            if not self.robot.is_steering():        # 바퀴가 구르기 시작한 때부터 시간을 잼
                self.phase, self.phase_end = "drive", now + self.steps[self.index][1]
        elif self.phase == "drive":
            if now >= self.phase_end:
                self.robot.stop()                   # 바퀴 정지 + 바퀴 방향 0°로 복귀
                self.phase = "settle"
        elif self.phase == "settle":
            if self.robot.is_stopped():
                self.phase, self.phase_end = "pause", now + self.pause_sec
        elif self.phase == "pause":
            if now >= self.phase_end:
                self.index += 1
                self.phase = "begin"

    def screen_text(self, state: str) -> str:
        """미션 중의 Text Screen 4줄 (한 줄 9자 이내).

            MOVE        지금 상태 (MOVE / GUIDE / RETURN)
            STEP 2/3    지금 단계
            ROTATE R    지금 동작
            STEERING    조향 상태 (READY / STEERING)
        """
        steer = "STEERING" if self.robot.is_steering() else "READY"
        if state in ("MOVE", "RETURN") and self.steps:
            i = min(self.index, len(self.steps) - 1)
            label = _ACTIONS[self.steps[i][0]][2]
            return f"{state}\nSTEP {i + 1}/{len(self.steps)}\n{label}\n{steer}"
        return f"{state}\n\n\n{steer}"


class Mission:
    """안내 미션의 상태 흐름: WAIT → MOVE → GUIDE → RETURN → WAIT."""

    def __init__(self, robot: Robot, route, guide_sec: float = 3.0,
                 pause_sec: float = 0.5, return_to_start: bool = True):
        self.robot = robot
        self.route = route                      # 출발한 자리에서 안내 지점까지 가는 길
        self.guide_sec = guide_sec              # 안내하는 시간(초)
        self.return_to_start = return_to_start  # 안내한 뒤 출발한 자리로 돌아올지
        self.runner = RouteRunner(robot, pause_sec)
        self.state = "WAIT"                     # 지금 상태: WAIT · MOVE · GUIDE · RETURN
        self.started_at = 0.0                   # 미션을 시작한 시각
        self.guide_end = 0.0                    # 안내를 끝낼 시각

    @property
    def running(self) -> bool:
        """미션이 진행 중이면 True (WAIT가 아니면)."""
        return self.state != "WAIT"

    def start(self, key: str = "5"):
        """5번 키: 멈춰 있으면 미션을 시작합니다."""
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
        """0번 키: 미션을 멈추고 대기 상태로 돌아갑니다. 로봇 정지는 호출하는 쪽에서 합니다."""
        if not self.running:
            return
        self.runner.stop()
        self.robot.hide_guide()
        self.robot.screen_override = None
        self._change("WAIT", f"stopped (key {key})")

    def update(self):
        """메인 루프에서 매 반복마다 부릅니다. 상태가 끝났으면 다음 상태로 넘어갑니다."""
        now = _now()
        if self.state == "MOVE":                     # 이동: 경로를 다 달리면 안내
            if self.runner.done:
                self._change("GUIDE", f"showing guide {self.guide_sec:.1f}s")
                self.robot.show_guide()
                self.guide_end = now + self.guide_sec
        elif self.state == "GUIDE":                  # 안내: 정한 시간이 지나면 복귀
            if now >= self.guide_end:
                self.robot.hide_guide()
                if self.return_to_start:
                    self._change("RETURN", "same route in reverse")
                    self.runner.start(reverse_route(self.route), "RETURN")
                else:
                    self._finish(now)
        elif self.state == "RETURN":                 # 복귀: 되짚어 오면 미션 완료
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
