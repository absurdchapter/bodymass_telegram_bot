import csv
import os
import typing as t
import uuid
from codecs import iterdecode
from datetime import datetime, timedelta

import aiosqlite
import numpy as np
import requests
from matplotlib import pyplot
from matplotlib.dates import date2num, DateFormatter

from src.datautils import sqlite_db_path, date_format
from src.datautils.challenge import Challenge, get_active_challenge

sqlite_db_users_mass = 'users_mass'
csv_tmp_folder = 'data/tmp/'
csv_tmp_filename_template = 'bodymass_{user_id}_{hash}.csv'
csv_uploaded_tmp_filename_template = 'uploaded_{user_id}_{hash}.csv'
plot_tmp_folder = 'data/tmp/'
plot_tmp_filename_template = '{user_id}_{hash}.png'


async def add_bodymass_record_now(user_id: int, body_mass: float) -> None:
    await add_bodymass_record(user_id, datetime.now().date(), body_mass)


async def add_bodymass_record(user_id: int, date: datetime.date, body_mass: float) -> None:
    async with aiosqlite.connect(sqlite_db_path) as db:
        query = f"INSERT INTO {sqlite_db_users_mass} (user_id, date, body_mass) " \
                f"VALUES ('{user_id}', '{date.strftime(date_format)}', {body_mass}); "

        await db.execute(query)
        await db.commit()


async def delete_user_bodymass_data(user_id: int) -> None:
    async with aiosqlite.connect(sqlite_db_path) as db:
        await db.execute(f"DELETE FROM {sqlite_db_users_mass} WHERE user_id = '{user_id}'")
        await db.commit()


async def fetch_user_bodymass_data(user_id: int):
    async with aiosqlite.connect(sqlite_db_path) as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"SELECT date, body_mass FROM {sqlite_db_users_mass} "
                                 f"WHERE user_id = '{user_id}' ORDER BY date ASC")
            while row := await cursor.fetchone():
                yield row


def random_hash() -> str:
    """Returns a random 8-piece hash"""
    return uuid.uuid4().hex[:8]


async def plot_user_bodymass_data(user_id: int, *,
                                  only_two_weeks: bool = False,
                                  only_challenge_range: bool = False,
                                  plot_label: str = 'Bodyweight, kg',
                                  ignore_challenge: bool = False
                                  ) \
        -> tuple[str, t.Optional[np.array], float]:
    """Plot user data to an image.

    Keyword arguments:
    :param user_id: user id
    :param only_two_weeks: draw progress only for the past 2 weeks
    :param only_challenge_range: draw only challenge range (cannot be used with only_two_weeks)
    :param plot_label: plot label
    :param ignore_challenge: if True, challenge will be ignored

    :return: image temporary file path, speed kg/week, mean body mass
    """
    if only_challenge_range and only_two_weeks:
        raise AttributeError("only_challenge_range cannot be used with only_two_weeks")

    os.makedirs(plot_tmp_folder, exist_ok=True)
    plot_file_path = os.path.join(plot_tmp_folder,
                                  plot_tmp_filename_template.format(user_id=user_id, hash=random_hash()))

    date_list: list[datetime] = []
    mass_list: list[float] = []
    async for (date_str, body_mass) in fetch_user_bodymass_data(user_id):
        datetime_object = datetime.strptime(date_str, date_format)

        date_list.append(datetime_object)
        mass_list.append(body_mass)

    challenge = None
    if not ignore_challenge:
        challenge = await get_active_challenge(user_id)

    date_limits = None
    if only_two_weeks:
        date_limits = datetime.now() - timedelta(days=14), datetime.now()
    if only_challenge_range:
        date_limits = (datetime.strptime(challenge.start_date, date_format),
                       datetime.strptime(challenge.end_date, date_format))

    regression_coef = draw_plot_bodymass(date_list, mass_list, plot_file_path, plot_label,
                                         challenge=challenge,
                                         date_limits=date_limits)
    speed_kg_week = round(regression_coef[0] * 7, 2) if regression_coef is not None else None
    if len(mass_list) < 4:
        speed_kg_week = None

    return plot_file_path, speed_kg_week, float(np.mean(mass_list))


def desired_regression(challenge: Challenge):
    y = challenge.start_weight, challenge.target_weight
    x = list(map(date2num, [datetime.strptime(challenge.start_date, date_format),
                            datetime.strptime(challenge.end_date, date_format)]))
    coef = np.polyfit(x, y, 1)
    func = np.poly1d(coef)
    return x, func(x)


def filter_dates(date_filter: t.Callable[[datetime], bool],
                 date: t.Iterable[datetime],
                 mass: t.Iterable[float]) -> tuple[t.Iterable[datetime], t.Iterable[float]]:
    filtered_date = []
    filtered_mass = []

    for date_elem, mass_elem in zip(date, mass):
        if date_filter(date_elem):
            filtered_date.append(date_elem)
            filtered_mass.append(mass_elem)

    return filtered_date, filtered_mass


def draw_plot_bodymass(date: t.Iterable[datetime], mass: list[float], file_path: str, plot_label: str,
                       challenge: Challenge | None = None,
                       start_label: str = 'Start',
                       target_label: str = 'Goal',
                       date_limits: t.Optional[tuple[datetime, datetime]] = None) -> t.Optional[np.array]:
    if date_limits:
        def fits_limits(datetime_obj: datetime) -> bool:
            return date_limits[0] <= datetime_obj <= date_limits[1]
        date, mass = filter_dates(fits_limits, date, mass)

    x = list(map(date2num, date))
    y = mass

    regression_coef = np.polyfit(x, y, 1) if len(x) > 1 else None
    regression_func = np.poly1d(regression_coef) if len(x) > 1 else None

    fig, ax = pyplot.subplots(figsize=[8, 5])

    if challenge:
        desired_x, desired_y = desired_regression(challenge)
        pyplot.plot(desired_x, desired_y, linestyle='dashed', color='red', markevery=[0, -1], marker='x')

        def annotate(label, x_, y_):
            pyplot.annotate(label, (x_, y_), color='red', ha='center', va='top',
                            xytext=(0, -5), textcoords="offset points")

        annotate(f'{start_label}', desired_x[0], desired_y[0])
        annotate(f'{target_label}', desired_x[1], desired_y[1])

    pyplot.ylim(*_get_y_limits(challenge, y))
    pyplot.xlim(*_get_x_limits(date_limits, x))

    pyplot.scatter(x, y)

    if len(x) > 1:
        pyplot.plot(x, regression_func(x))

    pyplot.ylabel(plot_label)

    ax.xaxis.set_major_formatter(DateFormatter('%d %b'))
    pyplot.xticks(rotation=45)
    pyplot.grid()
    pyplot.tight_layout()

    pyplot.savefig(file_path, dpi=300)
    pyplot.close('all')

    return regression_coef


def _get_y_limits(challenge: t.Optional[Challenge], y: t.Sequence[float]) -> t.Sequence[float]:
    """
    :returns: arguments for pyplot.ylim()
    """
    if len(y) > 1:
        return min(y) // 5 * 5 - 6, max(y) // 5 * 5 + 6
    elif challenge is None:
        return 64, 76
    return []


def _get_x_limits(date_limits: t.Optional[tuple[datetime, datetime]], x: t.Sequence[float]) -> t.Sequence[float]:
    """
    :returns: arguments for pyplot.xlim()
    """
    if not date_limits:
        return []

    min_x = date2num(date_limits[0])
    max_x = date2num(date_limits[1])
    if len(x) > 0:
        min_x = max(min_x, min(x)) - 1
        max_x = min(max_x, max(x)) + 1

    return min_x, max_x


async def user_bodymass_data_to_csv(user_id: int) -> str:
    """Save user data from the database to a csv file.

    Keyword arguments:
    :param user_id: user id

    :return csv temporary file path
    """

    os.makedirs(csv_tmp_folder, exist_ok=True)
    csv_file_path = os.path.join(csv_tmp_folder,
                                 csv_tmp_filename_template.format(user_id=user_id, hash=random_hash()))
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file_object:
        csv_writer = csv.writer(csv_file_object)
        async for row in fetch_user_bodymass_data(user_id):
            csv_writer.writerow(row)

    return csv_file_path


class CSVParsingError(Exception):
    pass


async def user_bodymass_data_from_csv_url(user_id: int, csv_url: str, max_body_weight: int) -> None:
    with requests.get(csv_url) as request:
        csv_reader = csv.reader(iterdecode(request.iter_lines(), 'utf-8'))
        for row in csv_reader:
            try:
                date, body_weight = row
                date = datetime.strptime(date, date_format)
                body_weight = float(body_weight)
                assert 0 < body_weight < max_body_weight
            except Exception:
                raise CSVParsingError()

            await add_bodymass_record(user_id, date, body_weight)
