import inspect
import typing as t
from datetime import datetime
from functools import wraps
from pathlib import Path

from src.datautils.bodymass import draw_plot_bodymass
from src.datautils.challenge import Challenge

SAVE_DIR = 'data/tmp'

# TODO assert regression coeffs

def _get_funcname() -> str:
    return inspect.stack()[1][3]


def _get_file_path(funcname: str):
    return str(Path(SAVE_DIR) / (funcname + '.png'))

def test1():
    print(f"Running {_get_funcname()}...", )

    dates = [
        datetime(2021, 5, 1),
        datetime(2021, 5, 3),
        datetime(2021, 5, 4),
        datetime(2021, 5, 6),
        datetime(2021, 5, 7),
        datetime(2021, 5, 9)
    ]
    measurements = [
        100.5,
        100.2,
        101.1,
        98.8,
        98.6,
        99.5
    ]
    assert len(dates) == len(measurements)

    file_path = _get_file_path(_get_funcname())
    draw_plot_bodymass(dates, measurements, file_path, "Bodyweight, kg")
    print('Result saved to', file_path)


def test2():
    print(f"Running {_get_funcname()}...", )

    dates = [
        datetime(2021, 5, 1),
        datetime(2021, 5, 3),
        datetime(2021, 5, 4),
        datetime(2021, 5, 6),
        datetime(2021, 5, 7),
        datetime(2021, 5, 9)
    ]
    measurements = [
        100.5,
        100.2,
        101.1,
        98.8,
        98.6,
        99.5
    ]
    assert len(dates) == len(measurements)

    file_path = _get_file_path(_get_funcname())
    draw_plot_bodymass(dates, measurements, file_path, "Bodyweight, kg")
    print('Result saved to', file_path)


def test3():
    print(f"Running {_get_funcname()}...", )

    dates = [
        datetime(2021, 5, 1),
        datetime(2021, 5, 3),
        datetime(2021, 5, 4),
        datetime(2021, 5, 6),
        datetime(2021, 5, 7),
        datetime(2021, 5, 9)
    ]
    measurements = [
        100.5,
        100.2,
        101.1,
        98.8,
        98.6,
        99.5
    ]
    challenge = Challenge(
        challenge_id=0,
        user_id="",
        is_active=True,

        start_date="2021/04/30",
        end_date="2021/05/10",

        start_weight=101,
        target_weight=99
    )

    assert len(dates) == len(measurements)

    file_path = _get_file_path(_get_funcname())
    draw_plot_bodymass(dates, measurements, file_path, "Bodyweight, kg", challenge)
    print('Result saved to', file_path)


def main():
    test1()
    test2()
    test3()


if __name__ == "__main__":
    main()