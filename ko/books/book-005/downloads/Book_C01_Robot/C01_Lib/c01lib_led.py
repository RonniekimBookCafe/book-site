# -*- coding: utf-8 -*-
"""
c01lib_led.py  |  CORE-01 교육용 라이브러리 · Input LED 색
배포 버전 1.6.3

Input LED의 색을 로봇의 동작에 맞춰 바꿉니다.

키를 누를 때 LED가 반짝이는 동작(Pulse)은 RoboCo의 Controls Mapping이
맡고, 이 코드는 색(color)만 바꿉니다. 그래서 turn_on()·turn_off()는
부르지 않습니다. 한 LED에서 Pulse는 Controls Mapping이, 색은 Python이
맡습니다.

알아 두기: RoboCo API의 알려진 문제
Color.from_hex("black")은 Color가 아니라 함수를 돌려주어,
led.color = "black" 처럼 쓰면 오류가 납니다. 그래서 이 파일에서는
검정(꺼진 느낌의 색)이 필요할 때 Color(0, 0, 0)을 직접 씁니다.
"red", "green", "white" 같은 다른 색 이름은 정상적으로 동작합니다.
"""

from controllables import LED
from color import Color
from . import c01lib_ports as ports

# 동작별 LED 색. 정지는 검정 Color(0, 0, 0)입니다
# ("black" 이름은 위의 이유로 쓰지 않습니다).
_STATE_COLORS = {
    "idle": Color(0, 0, 0),
    "forward": Color.green(),
    "backward": Color.red(),
    "turn_left": Color(0.0, 0.4, 1.0),
    "turn_right": Color(0.0, 0.4, 1.0),
    "pivot_left": Color(0.6, 0.0, 1.0),
    "pivot_right": Color(0.6, 0.0, 1.0),
    "diagonal_left": Color(1.0, 0.6, 0.0),
    "diagonal_right": Color(1.0, 0.6, 0.0),
}
_DEFAULT_COLOR = Color(1.0, 1.0, 1.0)  # 표에 없는 동작은 흰색


class InputLED:
    """Input LED 한 개의 색만 다루는 클래스.

    LED의 Pulse(반짝임)는 Controls Mapping이 맡으므로 다루지 않습니다.
    """

    def __init__(self):
        self.led = LED(ports.PORT_INPUT_LED)

    def set_color(self, state_name: str):
        """동작 이름(state_name)에 맞는 색으로 LED 색을 바꿉니다.
        표에 없는 이름이면 흰색으로 바꿉니다.
        """
        self.led.color = _STATE_COLORS.get(state_name, _DEFAULT_COLOR)
