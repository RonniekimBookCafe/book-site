# -*- coding: utf-8 -*-
"""
c01lib_drive.py  |  CORE-01 교육용 라이브러리 · 바퀴 DC 모터 4개 묶음
배포 버전 1.6.3

FL·FR·RL·RR 네 바퀴의 DC Motor를 한 묶음으로 다룹니다. 모터마다
Reference를 시작할 때 한 번만 만들고, 이후에는 같은 Reference를 계속
씁니다(동작할 때마다 새로 만들지 않음).

사용하는 RoboCo 공식 API (DCMotor)
- spin(power): 출력 비율로 회전. -1 ~ 1 (물리 속도 단위가 아닌 비율)
- stop(): 이 코드가 보낸 구동 신호를 해제
- flipped: 모터 회전 방향 뒤집기
- max_rpm, acceleration_time, brake_force, brake_time:
  모터 설정 값 (스크립트가 읽고 바꿈)
- max_torque: 모터 설정 값 (이 로봇에서는 고정값이므로 읽기만 함)

Robot(c01lib_robot.py)은 DCMotor를 직접 다루지 않고 이 파일의 함수만 부릅니다.
"""

from controllables import DCMotor
from . import c01lib_ports as ports

# 바퀴 속도는 Target RPM 하나로 정합니다.
# spin()에는 언제나 1.0(최대 비율)을 보내므로, 바퀴는 RoboCo 설정 창의
# Target RPM(스크립트의 TARGET_RPM)까지 돕니다. 같은 속도를 비율과 RPM
# 두 곳에서 곱해 정하지 않기 위해서입니다.
SPIN_RATIO = 1.0

# 스크립트가 바꾸는 모터 설정 값 네 가지.
#   화면 이름 → (API 속성 이름, 표시 형식, 영어 이름, 최솟값, 최댓값)
# 영어 이름과 최댓값은 RoboCo 설정 창(DC Motor)의 이름·범위와 같습니다.
# 순서도 설정 창과 같습니다.
MOTOR_SETTINGS = {
    "RPM":     ("max_rpm",           "{:.0f} rpm", "Target RPM",        0.0, 1000.0),
    "ACCEL":   ("acceleration_time", "{:.2f} s",   "Acceleration Time", 0.0, 10.0),
    "BRAKE F": ("brake_force",       "{:.1f}",     "Max Brake Force",   0.0, 1570.0),
    "BRAKE T": ("brake_time",        "{:.2f} s",   "Braking Time",      0.0, 10.0),
}

# 스크립트가 바꾸지 않고 읽어서 기록만 하는 모터 설정 값.
#   화면 이름 → (API 속성 이름, 표시 형식, 영어 이름)
# Max Torque는 이 로봇에서 6290으로 고정된 값입니다.
# 설정 창의 Start On은 Python API에 해당 속성이 없어 다루지 않습니다.
FIXED_SETTINGS = {
    "TORQUE":  ("max_torque",        "{:.0f}",     "Max Torque"),
}


def clamp_setting(name: str, value: float) -> float:
    """모터 설정 값을 RoboCo 설정 창의 범위(최솟값~최댓값) 안으로 맞춥니다."""
    _, _, _, low, high = MOTOR_SETTINGS[name]
    return min(max(value, low), high)


class DriveMotors:
    """네 바퀴 DC Motor를 하나의 구동 묶음으로 다루는 클래스."""

    def __init__(self):
        # 모터마다 Reference를 여기서 한 번만 만들고 계속 씁니다.
        self.fl = DCMotor(ports.PORT_FL_DRIVE)
        self.fr = DCMotor(ports.PORT_FR_DRIVE)
        self.rl = DCMotor(ports.PORT_RL_DRIVE)
        self.rr = DCMotor(ports.PORT_RR_DRIVE)
        self._all = (self.fl, self.fr, self.rl, self.rr)

    def apply_flip_settings(self):
        """시작할 때 한 번 호출해 모터 장착 방향 보정을 적용합니다."""
        self.fl.flipped = ports.FLIP_FL_DRIVE
        self.fr.flipped = ports.FLIP_FR_DRIVE
        self.rl.flipped = ports.FLIP_RL_DRIVE
        self.rr.flipped = ports.FLIP_RR_DRIVE

    # ------------------------------------------------------------
    # 바퀴 구동 패턴
    # 아래 네 가지 패턴만으로 W·S·A·D·Z·C·Q·E 여덟 개 키의 바퀴 구동을
    # 모두 표현합니다. 바퀴 방향(0°, ±45°)은 이 클래스가 아니라
    # c01lib_steering.SteeringServos가 맡습니다.
    # 네 패턴 모두 같은 SPIN_RATIO를 보내므로, 키마다 다른 것은 속도가
    # 아니라 바퀴마다 도는 방향(+ / -)입니다.
    # ------------------------------------------------------------
    def all_forward(self):
        """W·Q·E가 함께 쓰는 패턴: 네 바퀴 모두 전진."""
        for motor in self._all:
            motor.spin(SPIN_RATIO)

    def all_backward(self):
        """S가 쓰는 패턴: 네 바퀴 모두 후진."""
        for motor in self._all:
            motor.spin(-SPIN_RATIO)

    def left_back_right_forward(self):
        """A·Z가 함께 쓰는 패턴: 왼쪽 바퀴 후진 + 오른쪽 바퀴 전진.

        A는 바퀴 0°에서, Z는 바퀴 ±45°에서 이 같은 패턴을 씁니다. 두 키의
        차이는 모터 명령이 아니라 바퀴 방향에 있습니다. 같은 모터 명령도
        바퀴 방향에 따라 전혀 다른 움직임이 됩니다.
        """
        self.fl.spin(-SPIN_RATIO)
        self.rl.spin(-SPIN_RATIO)
        self.fr.spin(SPIN_RATIO)
        self.rr.spin(SPIN_RATIO)

    def left_forward_right_back(self):
        """D·C가 함께 쓰는 패턴: 왼쪽 바퀴 전진 + 오른쪽 바퀴 후진."""
        self.fl.spin(SPIN_RATIO)
        self.rl.spin(SPIN_RATIO)
        self.fr.spin(-SPIN_RATIO)
        self.rr.spin(-SPIN_RATIO)

    def read_setting(self, name: str) -> list:
        """네 모터의 설정 값(name)을 읽어 [FL, FR, RL, RR] 순서로 돌려줍니다.
        예: read_setting("max_rpm")
        """
        return [getattr(motor, name) for motor in self._all]

    def apply_setting(self, name: str, value: float):
        """네 모터의 설정 값(name)을 모두 value로 바꿉니다. 바로 적용됩니다.
        예: apply_setting("max_rpm", 150)
        """
        for motor in self._all:
            setattr(motor, name, value)

    def target_rpm(self) -> float:
        """지금 모터에 설정된 Target RPM을 돌려줍니다(FL 기준, 네 바퀴는 같은 값).
        측정한 회전수가 아니라 설정한 목표값입니다. 실험 키로 바꾼 값도 반영됩니다.
        """
        return self.fl.max_rpm

    def stop_all(self):
        """네 바퀴의 구동 신호를 모두 해제합니다.

        stop()은 이 코드가 보낸 구동 신호만 해제합니다. 로봇2
        (Book-CORE-01-SCRIPT)에서는 Controls Mapping이 DC Motor에 연결되어
        있지 않으므로, 이 stop()만으로 바퀴 구동이 멈춥니다.
        """
        for motor in self._all:
            motor.stop()
