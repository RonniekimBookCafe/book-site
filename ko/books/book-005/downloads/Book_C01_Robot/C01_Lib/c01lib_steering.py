# -*- coding: utf-8 -*-
"""
c01lib_steering.py  |  CORE-01 교육용 라이브러리 · 조향 서보 4개 묶음
배포 버전 1.6.3

네 바퀴의 Steering Servo를 한 묶음으로 다룹니다.

- 자세별 바퀴 각도: 기본 주행(0°), 제자리 회전(바퀴별 ±45°),
  왼쪽·오른쪽 대각선(네 바퀴 -45° / +45°)을 아래 표 하나로 관리합니다.
- 시간차 조향: 두 바퀴를 먼저 돌리고 나머지 두 바퀴를 나중에 돌려,
  네 바퀴를 한꺼번에 돌릴 때 차체가 틀어지는 것을 줄입니다.
- 천천히 조향: 목표 각도를 여러 번에 나누어 보내 서보가 한꺼번에 돌면서
  차체가 들썩이는 것을 막습니다(키를 뗄 때 0°로 돌아가는 동작에 사용).

사용하는 RoboCo 공식 API (ServoMotor)
- spin_to_degrees(angle): 목표 각도로 이동. 양수 = CW, 음수 = CCW
- limits_degrees: 허용 회전 범위. (ccw, cw) 순서이며 둘 다 양수

코드 안의 각도는 모두 "차체 기준(오른쪽 = 양수)"입니다. 서보에 실제로
보내는 부호는 c01lib_ports.STEERING_SIGN_* 로 바꿉니다.
"""

from controllables import ServoMotor
from . import c01lib_ports as ports

# ----------------------------------------------------------------
# 자세별 바퀴 조향각 (차체 기준, 단위 °) — 순서: FL, FR, RL, RR
# 차체 기준 각도는 "오른쪽 = 양수"입니다. 서보에 실제로 보내는 부호는
# c01lib_ports.STEERING_SIGN_* 가 맞추므로, 이 표는 서보를 어떻게
# 달았는지와 관계없이 설계한 각도 그대로 둡니다.
# ----------------------------------------------------------------
_POSTURE_ANGLES = {
    # W·S·A·D 기본 주행: 네 바퀴 0°
    "drive": (0.0, 0.0, 0.0, 0.0),
    # Z·C 제자리 회전: 네 바퀴가 차체 중심을 도는 원을 따라 굴러가도록
    # 앞바퀴 두 개와 뒷바퀴 두 개가 각각 서로를 향해 45° 꺾임
    "pivot": (45.0, -45.0, -45.0, 45.0),
    # Q 왼쪽 대각선: 네 바퀴가 10시 방향
    "diag_left": (-45.0, -45.0, -45.0, -45.0),
    # E 오른쪽 대각선: 네 바퀴가 2시 방향
    "diag_right": (45.0, 45.0, 45.0, 45.0),
}

# ----------------------------------------------------------------
# 시간차 조향 순서 — 먼저 돌릴 두 바퀴, 나중에 돌릴 두 바퀴
# (바퀴 번호: 0=FL, 1=FR, 2=RL, 3=RR)
#
# 네 바퀴를 한꺼번에 돌리면 네 바퀴가 모두 바닥에 끌려, 차체를 붙잡아
# 줄 바퀴가 없습니다. 두 바퀴씩 나누어 돌리면 한 번에 끌리는 바퀴가
# 줄고, 가만히 있는 두 바퀴가 바닥을 붙잡아 차체가 틀어지는 것을
# 줄여 줍니다.
# ----------------------------------------------------------------
_STAGGER_ORDERS = {
    "front_rear": ((0, 1), (2, 3)),   # 앞바퀴 두 개 → 뒷바퀴 두 개
    "diagonal": ((0, 3), (1, 2)),     # FL·RR → FR·RL (마주 보는 대각선끼리)
}


class SteeringServos:
    """네 바퀴 Steering Servo를 하나의 조향 묶음으로 다루는 클래스."""

    def __init__(self):
        self.fl = ServoMotor(ports.PORT_FL_STEER)
        self.fr = ServoMotor(ports.PORT_FR_STEER)
        self.rl = ServoMotor(ports.PORT_RL_STEER)
        self.rr = ServoMotor(ports.PORT_RR_STEER)
        self._all = (self.fl, self.fr, self.rl, self.rr)
        self._signs = (ports.STEERING_SIGN_FL, ports.STEERING_SIGN_FR,
                       ports.STEERING_SIGN_RL, ports.STEERING_SIGN_RR)

        # 마지막으로 요청한 자세. 같은 자세를 반복해서 보내지 않기 위해 기억합니다.
        self._current_posture = None  # "drive" | "pivot" | "diag_left" | "diag_right"

        # 시간차 조향에서 아직 보내지 않은 나머지 두 바퀴
        self._pending_group = None    # 바퀴 번호 두 개
        self._pending_angles = None   # 그 자세의 네 바퀴 각도
        self._pending_at = 0.0        # 보낼 시각

        # 네 바퀴에 마지막으로 보낸 각도(차체 기준). 천천히 조향할 때
        # 출발 각도로 씁니다. 아직 한 번도 보내지 않았으면 None 입니다.
        self._last_angles = [None, None, None, None]

        # 천천히 조향(각도를 나누어 보내기)의 진행 정보
        self._ramp = None             # (출발 각도, 목표 각도, 시작 시각, 끝 시각)

    def apply_flip_settings(self):
        """시작할 때 한 번 호출해 서보 장착 방향 보정을 적용합니다."""
        self.fl.flipped = ports.FLIP_FL_STEER
        self.fr.flipped = ports.FLIP_FR_STEER
        self.rl.flipped = ports.FLIP_RL_STEER
        self.rr.flipped = ports.FLIP_RR_STEER

    def apply_limits(self):
        """시작할 때 한 번 호출해 네 서보의 허용 회전 범위를 똑같이
        설정합니다. limits_degrees는 (ccw, cw) 순서이며 둘 다 양수입니다.
        """
        limits = (ports.STEERING_LIMIT_CCW_DEG, ports.STEERING_LIMIT_CW_DEG)
        for servo in self._all:
            servo.limits_degrees = limits

    def _send_wheel(self, index: int, body_angle_deg: float):
        """차체 기준 각도 하나를 해당 서보의 실제 부호로 바꿔 보냅니다."""
        self._all[index].spin_to_degrees(body_angle_deg * self._signs[index])
        self._last_angles[index] = body_angle_deg

    def begin_posture(self, name: str, now: float,
                      second_group_delay_sec: float = 0.0,
                      order: str = "front_rear",
                      ramp_sec: float = 0.0) -> bool:
        """조향 자세를 바꿉니다.

        - 먼저 돌릴 두 바퀴는 지금 바로 조향합니다.
        - 나머지 두 바퀴는 second_group_delay_sec 뒤에 조향합니다.
          이 값이 0이면 네 바퀴를 한꺼번에 조향합니다.
        - order 는 "front_rear"(앞 → 뒤) 또는 "diagonal"(대각선끼리)입니다.
        - ramp_sec 가 0보다 크면 네 바퀴를 함께, 목표 각도를 ramp_sec 동안
          나누어 보내며 천천히 조향합니다(이때 시간차는 쓰지 않습니다).
          서보가 최고 속도로 한꺼번에 돌 때 차체가 들썩이는 것을 막습니다.

        이미 같은 자세면 아무것도 하지 않고 False를, 새 자세를 시작했으면
        True를 돌려줍니다. True 는 "명령을 보내기 시작했다"는 뜻일 뿐,
        바퀴가 목표 각도에 도착했다는 뜻은 아닙니다.
        """
        if name == self._current_posture:
            return False
        angles = _POSTURE_ANGLES[name]
        self._pending_group = None   # 이전 자세의 남은 조향은 취소
        self._ramp = None
        if ramp_sec > 0 and None not in self._last_angles:
            start = tuple(self._last_angles)
            self._ramp = (start, angles, now, now + ramp_sec)
            self._current_posture = name
            return True
        first, second = _STAGGER_ORDERS[order]
        for i in first:
            self._send_wheel(i, angles[i])
        if second_group_delay_sec > 0:
            self._pending_group = second
            self._pending_angles = angles
            self._pending_at = now + second_group_delay_sec
        else:
            for i in second:
                self._send_wheel(i, angles[i])
            self._pending_group = None
        self._current_posture = name
        return True

    def update(self, now: float):
        """메인 루프에서 매 반복마다 호출합니다.
        - 시간차 조향: 보낼 시각이 되면 나머지 두 바퀴를 조향
        - 천천히 조향: 지금 시각에 맞는 중간 각도를 네 바퀴에 보냄
        """
        if self._pending_group is not None and now >= self._pending_at:
            for i in self._pending_group:
                self._send_wheel(i, self._pending_angles[i])
            self._pending_group = None

        if self._ramp is not None:
            start, target, t0, t1 = self._ramp
            f = 1.0 if now >= t1 else max(0.0, (now - t0) / (t1 - t0))
            # 천천히 출발해 천천히 도착하도록 진행률을 부드럽게 바꿉니다.
            eased = f * f * (3.0 - 2.0 * f)
            for i in range(4):
                self._send_wheel(i, start[i] + (target[i] - start[i]) * eased)
            if f >= 1.0:
                self._ramp = None
