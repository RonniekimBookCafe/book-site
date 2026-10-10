# -*- coding: utf-8 -*-
"""
c01lib_screen.py  |  CORE-01 교육용 라이브러리 · 화면 펼침·접힘 서보
배포 버전 1.6.3

1번 키를 누를 때마다 화면을 펼치거나 접는 Toggle Screen입니다.

"목표 상태"와 "실제 위치"를 구분합니다.
- 목표 상태: 스크립트가 마지막으로 요청한 상태(펼침 또는 접힘)
- 실제 위치: 서보가 지금 실제로 가 있는 각도
명령을 보낸 순간 두 값은 다를 수 있습니다. 서보가 도착할 때까지 시간이
걸리기 때문입니다.
"""

from controllables import ServoMotor
from . import c01lib_ports as ports


class ScreenFold:
    """화면을 펼치고 접는 Servo 한 개를 다루는 클래스."""

    def __init__(self, start_deployed: bool = False):
        self.servo = ServoMotor(ports.PORT_SCREEN_FOLD)
        # 목표 상태: 스크립트가 마지막으로 요청한 상태(True = 펼침).
        # 서보가 실제로 그 각도에 도착했는지와는 다를 수 있습니다.
        self._target_deployed = start_deployed

    def apply_limits(self):
        limits = (ports.SCREEN_FOLD_LIMIT_CCW_DEG,
                 ports.SCREEN_FOLD_LIMIT_CW_DEG)
        self.servo.limits_degrees = limits

    def initialize_posture(self):
        """시작할 때 한 번, 시작 목표 상태의 각도로 보냅니다."""
        angle = ports.SCREEN_DEPLOYED_DEG if self._target_deployed else ports.SCREEN_FOLDED_DEG
        self.servo.spin_to_degrees(angle)

    def deploy(self):
        """목표 상태를 '펼침'으로 정하고 서보를 그 각도로 보냅니다."""
        self._target_deployed = True
        self.servo.spin_to_degrees(ports.SCREEN_DEPLOYED_DEG)

    def fold(self):
        """목표 상태를 '접힘'으로 정하고 서보를 그 각도로 보냅니다."""
        self._target_deployed = False
        self.servo.spin_to_degrees(ports.SCREEN_FOLDED_DEG)

    def toggle(self):
        """1번 키를 한 번 누를 때마다 목표 상태를 뒤집습니다(펼침 ↔ 접힘).

        c01lib_app.py는 키를 누르는 순간에만 이 함수를 부릅니다. 그래서
        키를 길게 누르고 있어도 화면이 계속 펼쳐졌다 접혔다 하지 않습니다.
        """
        if self._target_deployed:
            self.fold()
        else:
            self.deploy()

    def is_target_deployed(self) -> bool:
        """목표 상태가 펼침이면 True를 돌려줍니다. 서보의 실제 위치가
        아니라 스크립트가 마지막으로 요청한 상태입니다.
        """
        return self._target_deployed
