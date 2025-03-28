import inspect
import math
import sys
from datetime import datetime
from pathlib import Path

import numpy

from src.datautils.bodymass import draw_plot_bodymass
from src.datautils.challenge import Challenge, get_desired_speed_per_week

SAVE_DIR = 'data/tmp'

# TODO assert regression coeffs

def _get_funcname() -> str:
    return inspect.stack()[1][3]


def _get_file_path(funcname: str):
    return str(Path(SAVE_DIR) / (funcname + '.png'))


def test_happy_no_challenge():
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


def test_happy_with_challenge():
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
        user_id="",
        is_active=True,

        start_date="2021/04/30",
        end_date="2021/05/10",

        start_weight=101,
        target_weight=99
    )

    assert len(dates) == len(measurements)

    desired_speed = get_desired_speed_per_week(challenge)
    assert math.isclose(desired_speed, -1.4)

    file_path = _get_file_path(_get_funcname())
    regression_coef = draw_plot_bodymass(dates, measurements, file_path, "Bodyweight, kg", challenge)
    assert numpy.allclose(regression_coef, [-2.26190476e-01, 4.34130714e+03])
    speed_kg_week = round(regression_coef[0] * 7, 2)
    assert speed_kg_week == -1.58
    print('Result saved to', file_path)


def test_challenge_with_data_limits():
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
        user_id="",
        is_active=True,

        start_date="2021/04/30",
        end_date="2021/05/10",

        start_weight=101,
        target_weight=99
    )

    date_limits = datetime(year=2021, month=5, day=2), datetime(year=2021, month=5, day=7)

    assert len(dates) == len(measurements)
    assert len(date_limits) == 2

    file_path = _get_file_path(_get_funcname())

    draw_plot_bodymass(dates, measurements, file_path, "Bodyweight, kg", challenge,
                       date_limits=date_limits)
    print('Result saved to', file_path)


def test_no_points():
    print(f"Running {_get_funcname()}...", )
    dates = []
    measurements = []
    assert len(dates) == len(measurements)

    file_path = _get_file_path(_get_funcname())
    draw_plot_bodymass(dates, measurements, file_path, "Bodyweight, kg")
    print('Result saved to', file_path)


def test_no_points_with_challenge():
    print(f"Running {_get_funcname()}...", )
    dates = []
    measurements = []
    assert len(dates) == len(measurements)

    file_path = _get_file_path(_get_funcname())
    challenge = Challenge(
        user_id="",
        is_active=True,

        start_date="2021/04/30",
        end_date="2021/05/10",

        start_weight=101,
        target_weight=99
    )
    draw_plot_bodymass(dates, measurements, file_path, "Bodyweight, kg", challenge=challenge)
    print('Result saved to', file_path)


def test_no_points_with_challenge_and_limits():
    print(f"Running {_get_funcname()}...", )
    dates = []
    measurements = []
    assert len(dates) == len(measurements)
    challenge = Challenge(
        user_id="",
        is_active=True,

        start_date="2021/04/30",
        end_date="2021/05/10",

        start_weight=101,
        target_weight=99
    )
    date_limits = datetime(year=2021, month=5, day=2), datetime(year=2021, month=5, day=7)
    file_path = _get_file_path(_get_funcname())
    draw_plot_bodymass(dates, measurements, file_path, "Bodyweight, kg", challenge=challenge, date_limits=date_limits)
    print('Result saved to', file_path)


def test_one_point():
    print(f"Running {_get_funcname()}...", )
    dates = [
        datetime(2021, 5, 1),
    ]
    measurements = [
        100.5,
    ]
    file_path = _get_file_path(_get_funcname())
    draw_plot_bodymass(dates, measurements, file_path, "Bodyweight, kg")
    print('Result saved to', file_path)


def test_one_point_outside_date_limits():
    print(f"Running {_get_funcname()}...", )
    dates = [
        datetime(2021, 5, 1),
    ]
    measurements = [
        100.5,
    ]
    date_limits = datetime(year=2021, month=5, day=3), datetime(year=2021, month=5, day=7)
    file_path = _get_file_path(_get_funcname())
    draw_plot_bodymass(dates, measurements, file_path, "Bodyweight, kg", date_limits=date_limits)
    print('Result saved to', file_path)


def test_one_point_outside_date_limits_with_challenge():
    print(f"Running {_get_funcname()}...", )
    dates = [
        datetime(2021, 5, 1),
    ]
    measurements = [
        100.5,
    ]
    challenge = Challenge(
        user_id="",
        is_active=True,

        start_date="2021/04/30",
        end_date="2021/05/10",

        start_weight=101,
        target_weight=99
    )
    date_limits = datetime(year=2021, month=5, day=3), datetime(year=2021, month=5, day=7)
    file_path = _get_file_path(_get_funcname())
    draw_plot_bodymass(dates, measurements, file_path, "Bodyweight, kg", date_limits=date_limits, challenge=challenge)
    print('Result saved to', file_path)


def test_two_points():
    print(f"Running {_get_funcname()}...", )

    dates = [
        datetime(2021, 5, 1),
        datetime(2021, 5, 3),
    ]
    measurements = [
        100.5,
        100.5
    ]
    assert len(dates) == len(measurements)

    file_path = _get_file_path(_get_funcname())
    draw_plot_bodymass(dates, measurements, file_path, "Bodyweight, kg")
    print('Result saved to', file_path)


def main():
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isfunction(obj) and name.startswith('test_'):
            obj()


if __name__ == "__main__":
    main()
