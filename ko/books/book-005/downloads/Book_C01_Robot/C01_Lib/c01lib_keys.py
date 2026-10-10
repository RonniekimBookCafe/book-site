# -*- coding: utf-8 -*-
"""
c01lib_keys.py  |  CORE-01 교육용 라이브러리 · 키 입력
배포 버전 1.6.3

키보드 입력을 두 가지 방식으로 읽습니다.

- 주행 키 (W·S·A·D·Z·C·Q·E): 누르고 있는 동안 동작합니다. 여러 키를
  함께 누르면 가장 나중에 누른 키를 따르고, 모두 떼면 멈춥니다.
- 명령 키 (1·0·2·3·4·5): 누르는 순간 한 번만 동작합니다. 길게 눌러도
  반복하지 않습니다.

사용하는 RoboCo 공식 API
- Input.stream(key): 키를 누를 때 True, 뗄 때 False를 한 번씩 알려 줍니다.
"""

from inputs import Input


def pressed(stream) -> bool:
    """명령 키가 눌렸으면 True. 쌓인 입력을 모두 읽어 비웁니다."""
    down = False
    for event in stream:
        if event:
            down = True
    return down


class DriveKeys:
    """주행 키 여러 개를 읽어, 지금 따라야 할 동작을 정하는 클래스."""

    def __init__(self, key_actions: dict):
        """key_actions: {키: 눌렀을 때 부를 동작} 예) {"w": robot.forward}"""
        self.keys = [(key, Input.stream(key), action) for key, action in key_actions.items()]
        self.held = []      # 지금 누르고 있는 키 (누른 순서대로)

    def update(self, on_release_all, blocked=None):
        """주행 키의 누름과 뗌을 처리합니다. 메인 루프에서 매번 부릅니다.

        on_release_all: 모든 키를 뗐을 때 부를 동작 (예: robot.stop)
        blocked       : 키를 받지 않을 때 부를 함수. 누른 키 이름을 받습니다.
                        None이면 키를 정상적으로 받습니다.
        """
        for entry in self.keys:
            key, stream, action = entry
            for event in stream:
                if blocked is not None:          # 키를 받지 않는 중 (예: 미션 중)
                    if entry in self.held:
                        self.held.remove(entry)
                    if event:
                        blocked(key)
                    continue
                if event:                        # 누름
                    action()
                    if entry not in self.held:
                        self.held.append(entry)
                else:                            # 뗌
                    if entry in self.held:
                        self.held.remove(entry)
                    if self.held:
                        self.held[-1][2]()       # 아직 누르고 있는 키 중 가장 나중 키를 따름
                    else:
                        on_release_all()

    def clear(self):
        """누르고 있던 키를 모두 잊습니다. 다시 눌러야 움직입니다(RESET 뒤)."""
        self.held.clear()
