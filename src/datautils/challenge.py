import dataclasses
import typing as t
from datetime import datetime
from decimal import Decimal

import aiosqlite

from src.datautils import date_format, sqlite_db_path

sqlite_db_users_challenges = 'users_challenges'


@dataclasses.dataclass
class Challenge:
    user_id: str = ''
    is_active: int = 0

    start_date: str = ''
    end_date: str = ''

    start_weight: float = 0
    target_weight: float = 0

    def date_filter(self) -> t.Callable[[datetime], bool]:
        def func(datetime_object: datetime) -> bool:
            return datetime.strptime(self.start_date, date_format) <= datetime_object <= datetime.strptime(
                self.end_date, date_format)

        return func

    @classmethod
    def represent_column_for_sql(cls, value, column: str):
        if column in ['user_id', 'start_date', 'end_date']:
            return f"'{value}'"
        if column in ['is_active']:
            return f"{int(value)}"
        if column in ['start_weight', 'target_weight']:
            return f"{float(value)}"


def get_desired_speed_per_week(challenge: Challenge) -> float:
    """
    :raises: ZeroDivisionError in case challenge.end_date == challenge.start_date
    :raises: ValueError if challenge dates are invalid
    """
    delta = datetime.strptime(challenge.end_date, date_format) - datetime.strptime(challenge.start_date, date_format)
    delta_weeks = delta.total_seconds() / (60*60*24*7)
    delta_kg = challenge.target_weight - challenge.start_weight

    return delta_kg / delta_weeks


async def get_challenges(user_id: int) -> list[Challenge]:
    async with aiosqlite.connect(sqlite_db_path) as db:
        async with db.cursor() as cursor:
            query = f"SELECT user_id, is_active, start_date, end_date, start_weight, target_weight " \
                    f"FROM {sqlite_db_users_challenges} " \
                    f"WHERE user_id = '{user_id}';"
            await cursor.execute(query)
            challenges = [Challenge(*challenge) for challenge in await cursor.fetchall()]

            return challenges


async def get_challenge(user_id: int) -> t.Optional[Challenge]:
    challenges = await get_challenges(user_id)
    if len(challenges) == 0:
        return None

    result = challenges[-1]
    assert int(result.user_id) == int(user_id), "user_id mismatch in the database"

    return result


async def delete_challenges(user_id: int):
    async with aiosqlite.connect(sqlite_db_path) as db:
        await db.execute(f"DELETE FROM {sqlite_db_users_challenges} WHERE user_id = '{user_id}'")
        await db.commit()


async def get_active_challenge(user_id: int) -> t.Optional[Challenge]:
    challenge = await get_challenge(user_id)
    try:
        return challenge if challenge.is_active else None
    except AttributeError:
        return


async def insert_challenge(challenge: Challenge) -> None:
    columns = 'user_id', 'is_active', 'start_date', 'end_date', 'start_weight', 'target_weight'
    async with aiosqlite.connect(sqlite_db_path) as db:
        columns_joined: str = ', '.join(columns)
        values_for_sql = [Challenge.represent_column_for_sql(getattr(challenge, col), col) for col in columns]
        values_joined: str = ', '.join(values_for_sql)
        query = f"INSERT INTO {sqlite_db_users_challenges} ({columns_joined}) " \
                f"VALUES ({values_joined}); "

        await db.execute(query)
        await db.commit()


async def get_challenge_not_none(user_id: int):
    challenge = await get_challenge(user_id)
    if challenge is None:
        challenge = Challenge(user_id=str(user_id))
    return challenge
