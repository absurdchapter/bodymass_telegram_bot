import dataclasses
from datetime import datetime
import typing as t

from src.datautils import date_format


@dataclasses.dataclass
class Challenge:
    challenge_id: int

    user_id: str
    is_active: bool

    start_date: str
    end_date: str

    start_weight: float
    target_weight: float

    def date_filter(self) -> t.Callable[[datetime], bool]:
        def func(datetime_object: datetime) -> bool:
            return self.start_date_object() <= datetime_object <= self.end_date_object()
        return func

    def start_date_object(self) -> datetime:
        return datetime.strptime(self.start_date, date_format)

    def end_date_object(self) -> datetime:
        return datetime.strptime(self.end_date, date_format)
