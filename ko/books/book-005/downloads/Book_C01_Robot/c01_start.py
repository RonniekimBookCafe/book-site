# -*- coding: utf-8 -*-
"""
c01_start.py  |  CORE-01 시작 파일
배포 버전 1.6.3  |  로봇 파일 Book-CORE-01-SCRIPT(로봇2)에 연결해 실행합니다.

이 파일 하나로 책의 모든 실습을 합니다.
    PART 1~3  W·S·A·D·Z·C·Q·E로 주행, 1번 키로 화면 펼침·접힘
    PART 4    2·3·4 키로 바퀴 모터 설정 값을 바꿔 비교 (실험)
    PART 5    5번 키로 안내 미션 시작
    언제든    0번 키로 전체 RESET (헷갈리면 0)

이 파일에는 바꿔 볼 값과 키 배정만 모여 있습니다. 로봇을 움직이는 코드는
C01_Lib 폴더의 라이브러리에 있습니다.
"""

# --- 준비 코드: 이 부분은 바꾸지 않습니다 ------------------------------------
# 스크립트를 실행할 때마다 C01_Lib 라이브러리를 새로 읽어 옵니다. 라이브러리
# 파일을 고쳤을 때 고친 내용이 바로 반영되게 하기 위해서입니다. 파일을 지우는
# 것이 아니라, RoboCo가 기억해 둔 이전 내용만 비웁니다.
import sys as _sys

_sys.dont_write_bytecode = True  # 실행할 때 임시 파일(__pycache__ 폴더)을 만들지 않음

for _mod_name in list(_sys.modules.keys()):
    if _mod_name == "Book_C01_Robot" or _mod_name.startswith("Book_C01_Robot."):
        del _sys.modules[_mod_name]

from Book_C01_Robot.C01_Lib.c01lib_app import RobotApp


# ========================================
# 1. CONTROL PARAMETERS  (먼저 바꿔 볼 값)
# ========================================
# --- 바퀴 모터 설정: RoboCo 설정 창(DC Motor)과 같은 이름·범위 ---
#     스크립트를 시작하면 네 바퀴에 이 값을 적용합니다. PART 4 실험의 기준값입니다.
#     주행 속도는 TARGET_RPM 하나로 정하며, 여덟 주행 키가 모두 같은 값을 씁니다.
TARGET_RPM = 120             # 바퀴 목표 회전수 (0~1000)
ACCELERATION_TIME = 0.5      # 출발할 때 Target RPM까지 걸리는 시간(초, 0~10)
MAX_BRAKE_FORCE = 50         # 멈출 때의 제동력 (0~1570)
BRAKING_TIME = 0.2           # 멈출 때 제동이 걸리는 시간(초, 0~10)
# Max Torque(6290)는 고정값이라 바꾸지 않습니다. Start On(ON)은 Python API에
# 해당 속성이 없어, 두 값 모두 로봇 파일의 설정을 그대로 씁니다.

# --- 조향: 바퀴 방향을 바꿀 때의 시간(초) ---
STEERING_SETTLE_SEC = 0.5    # 바퀴 방향을 바꾼 뒤 바퀴를 돌리기까지 기다리는 시간
STEERING_STAGGER_SEC = 0.3   # 앞바퀴를 먼저 돌리고 뒷바퀴를 돌리기까지의 시간
RELEASE_RETURN_SEC = 0.6     # 키를 뗄 때 바퀴를 0°로 천천히 되돌리는 시간

# --- 화면과 기록 ---
GUIDE_MESSAGE = "WELCOME"    # 안내 문구 (한 줄 9자·4줄 이내, 줄바꿈은 "\n")
LOG_LEVEL = 1                # 콘솔 기록 양: 0 적게 · 1 보통 · 2 주행 동작까지


# ========================================
# 2. KEYS  (키 배정)
#    키를 바꾸면 로봇 파일의 Controls Mapping에도 같은 키를 넣습니다.
# ========================================
DRIVE_KEYS = {               # 누르고 있는 동안 동작
    "w": "forward",          # 전진
    "s": "backward",         # 후진
    "a": "turn_left",        # 왼쪽 방향 전환
    "d": "turn_right",       # 오른쪽 방향 전환
    "z": "rotate_left",      # 제자리 좌회전
    "c": "rotate_right",     # 제자리 우회전
    "q": "diagonal_left",    # 왼쪽 대각선 전진
    "e": "diagonal_right",   # 오른쪽 대각선 전진
}
COMMAND_KEYS = {             # 누르는 순간 한 번 동작
    "1": "toggle_screen",    # 화면 펼침·접힘 (접으면 0과 같은 전체 RESET)
    "0": "reset",            # 전체 RESET (헷갈리면 0)
    "2": "next_parameter",   # PART 4 실험할 값 고르기 (RPM → ACCEL → BRAKE F → BRAKE T)
    "3": "level_down",       # PART 4 한 단계 낮추기
    "4": "level_up",         # PART 4 한 단계 높이기
    "5": "start_mission",    # PART 5 안내 미션 시작
}


# ========================================
# 3. EXPERIMENT STEPS  (PART 4 실험 단계표)
#    값마다 LV 1 ~ LV 10의 값을 작은 값부터 적습니다. LV 10은 RoboCo 설정 창의 최댓값입니다.
#    기준값(1번 구역의 값)과 같은 단계가 기본 단계입니다.
#    2번 키를 누르면 위에서부터 차례로 고르고, 3·4로 한 단계씩 바꿉니다.
#    3·4로 바꾼 값은 2번으로 다른 값을 골라도 유지되고, 0 또는 1번(접기)으로 기준값이 됩니다.
# ========================================
EXPERIMENT_STEPS = [
    ("RPM",     [30, 60, 90, 120, 200, 300, 400, 600, 800, 1000]),     # TARGET_RPM (기준 LV 4)
    ("ACCEL",   [0.1, 0.2, 0.5, 1, 2, 3, 4, 6, 8, 10]),                # ACCELERATION_TIME (기준 LV 3)
    ("BRAKE F", [0, 25, 50, 100, 200, 400, 600, 900, 1200, 1570]),     # MAX_BRAKE_FORCE (기준 LV 3)
    ("BRAKE T", [0, 0.1, 0.2, 0.5, 1, 2, 4, 6, 8, 10]),                # BRAKING_TIME (기준 LV 3)
]


# ========================================
# 4. MISSION  (PART 5 안내 미션)
#    출발한 자리에서 안내 지점까지 가는 길을 (동작, 시간(초)) 순서로 적습니다.
#    동작: forward · backward · turn_left · turn_right · rotate_left · rotate_right · pause
# ========================================
MISSION_ROUTE = [
    ("forward",      2.0),   # 앞으로 2초
    ("rotate_right", 0.5),   # 제자리에서 오른쪽으로 0.5초 (약 90°, 기준값 RPM 120·ACCEL 0.5초일 때)
    ("forward",      1.5),   # 앞으로 1.5초
]
GUIDE_SEC = 3.0              # 안내 지점에서 화면을 펼치고 안내하는 시간(초)
STEP_PAUSE_SEC = 0.5         # 동작 하나를 마치고 다음 동작까지 쉬는 시간(초)
RETURN_TO_START = True       # 안내한 뒤 같은 길을 되짚어 출발한 자리로 돌아옴


# ========================================
# 5. RUN  (한 번 준비하고, 멈출 때까지 반복)
# ========================================
def main():
    app = RobotApp(globals())    # 준비: 위의 값과 키 배정을 로봇에 한 번 전달
    while app.running():         # 반복: 스크립트를 멈출 때까지
        app.update()             # 키 읽기 → 로봇 동작 → 화면·콘솔 표시
    app.shutdown()               # 마무리: 값을 기준값으로 되돌리고 모터 정지


if __name__ == "__main__":
    main()
