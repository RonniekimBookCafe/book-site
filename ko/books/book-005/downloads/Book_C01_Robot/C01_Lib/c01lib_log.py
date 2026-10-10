# -*- coding: utf-8 -*-
"""
c01lib_log.py  |  CORE-01 교육용 라이브러리 · 콘솔 LOG
배포 버전 1.6.3

콘솔 LOG는 "무슨 일이 언제 일어났는가"를 남기는 사건 기록입니다.
지금 상태(동작·출력·조향)는 로봇의 Text Screen이 보여 주므로, 콘솔에는
상태가 바뀐 사건만 짧게 남깁니다.

LOG는 로봇 화면·키 이름·RoboCo API와 같은 언어가 되도록 영어로 씁니다.
한 줄은 다음처럼 읽습니다.

    [  12.34s] STEER   Pivot posture (front → rear stagger)
     ────┬────  ──┬──   ───────────────┬───────────────
     시작 후     분류                 내용
     경과 시간

분류(category)는 대문자 한 낱말입니다.
    START  스크립트 시작          KEYS   키 안내
    SETUP  이번 실행의 설정값      STEER  바퀴 자세가 바뀜
    SCREEN 화면 펼침·접힘          DRIVE  주행 동작 요약 (LOG_LEVEL 2)
    EXP    실험 값 변경·RESET      STATE  안내 미션의 상태·단계
    END    스크립트 종료          ERROR  실행 중 오류
    NOTE   알림 (줄 수 제한 등)

기록할 양은 LOG_LEVEL 로 정합니다.
    0 : START·SETUP·END·ERROR 등 꼭 필요한 줄만
    1 : 0 + 바퀴 자세 변경, 화면 전환, 실험 값 변경, 미션 상태 (기본)
    2 : 1 + 주행 동작 (키를 뗄 때 "W forward | held 0.32s"처럼 한 줄)

콘솔에 줄이 계속 쌓이면 실행이 느려질 수 있으므로, LOG_MAX_LINES 줄을
넘으면 NOTE 한 줄을 남기고 출력을 멈춥니다. ERROR와 LOG_LEVEL 0의 줄은
이 제한과 관계없이 항상 출력합니다.
"""

from time import time as _time

_start_time = _time()
_level = 1
_max_lines = 200
_lines = 0
_stopped = False

# LOG 수준 (level 인자로 사용)
ALWAYS = 0   # 시작·설정·종료 등 꼭 필요한 줄
EVENT = 1    # 바퀴 자세 변경, 화면 전환, 실험 값 변경
DETAIL = 2   # 주행 동작 하나하나


def configure(level: int = 1, max_lines: int = 200):
    """시작 파일의 LOG_LEVEL, LOG_MAX_LINES 값을 적용합니다."""
    global _level, _max_lines
    _level = level
    _max_lines = max_lines


def header(title: str):
    """스크립트를 시작할 때 한 번, 무엇을 실행하는지와 읽는 법을 출력합니다."""
    print(f"==== {title} ====")
    print(f"  time = seconds since start | LOG_LEVEL {_level} | max {_max_lines} lines")


def _stamp() -> str:
    return f"[{_time() - _start_time:7.2f}s]"


def log(level: int, category: str, message: str):
    """콘솔에 사건 한 줄을 남깁니다.

    :param level: ALWAYS / EVENT / DETAIL 중 하나. LOG_LEVEL보다 크면 출력하지 않음
    :param category: 대문자 분류 한 낱말 (START, KEYS, SETUP, STEER, SCREEN,
                     DRIVE, EXP, STATE, END, ERROR, NOTE)
    :param message: 사람이 읽을 내용 (영어)
    """
    global _lines, _stopped
    always = category == "ERROR" or level == ALWAYS
    if level > _level and not always:
        return
    if _stopped and not always:
        return
    print(f"{_stamp()} {category:<6}  {message}")
    _lines += 1
    if _lines >= _max_lines and not _stopped:
        _stopped = True
        print(f"{_stamp()} {'NOTE':<6}  LOG reached {_max_lines} lines - further lines are hidden "
              "(ERROR and END are still shown)")
