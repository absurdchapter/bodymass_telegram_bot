from datetime import datetime
# noinspection PyProtectedMember
from src.datautils.bodymass import _get_date_limits
from src.datautils.challenge import Challenge
from freezegun import freeze_time


@freeze_time("2023-03-08")
def test_get_date_limits():
    INPUTS = [
        # Happy path
        {
            "challenge": Challenge(start_date="2023/02/10", end_date="2023/03/20"),
            "only_challenge_range": True,
            "only_two_weeks": False
        },
        {
            "challenge": Challenge(start_date="2023/02/10", end_date="2023/03/20"),
            "only_challenge_range": False,
            "only_two_weeks": True
        },
        {
            "challenge": Challenge(start_date="2023/02/10", end_date="2023/03/20"),
            "only_challenge_range": False,
            "only_two_weeks": False
        },
        # No challenge info
        {
            "challenge": None,
            "only_challenge_range": False,
            "only_two_weeks": False
        },
        {
            "challenge": None,
            "only_challenge_range": False,
            "only_two_weeks": True
        },
        {
            "challenge": None,
            "only_challenge_range": True,
            "only_two_weeks": False
        },

        # Range and two weeks
        {
            # Today is inside
            "challenge": Challenge(start_date="2023/03/02", end_date="2023/03/20"),
            "only_challenge_range": True,
            "only_two_weeks": True
        },
        {
            # Today is after
            "challenge": Challenge(start_date="2023/01/25", end_date="2023/02/20"),
            "only_challenge_range": True,
            "only_two_weeks": True
        },
        {
            # Today is after
            "challenge": Challenge(start_date="2023/03/12", end_date="2023/03/30"),
            "only_challenge_range": True,
            "only_two_weeks": True
        },
        {
            # challenge not present
            "challenge": None,
            "only_challenge_range": True,
            "only_two_weeks": True
        }
    ]

    EXPECTED_RESULTS = [
        # Happy path
        (datetime(2023, 2, 10,), datetime(2023, 3, 20)),
        (datetime(2023, 2, 22), datetime(2023, 3, 8)),
        None,

        # No challenge info
        None,
        (datetime(2023, 2, 22), datetime(2023, 3, 8)),
        None,

        # Range and two weeks
        (datetime(2023, 3, 2), datetime(2023, 3, 20)),
        (datetime(2023, 1, 25), datetime(2023, 2, 20)),
        (datetime(2023, 3, 12), datetime(2023, 3, 30)),
        (datetime(2023, 2, 22), datetime(2023, 3, 8)),


    ]

    for idx, [input_, expected_] in enumerate(zip(INPUTS, EXPECTED_RESULTS)):
        res = _get_date_limits(**input_)
        print(res)

        assert res == expected_, f"{idx}. inputs: {input_} \n {res} != {expected_}"


if __name__ == "__main__":
    test_get_date_limits()
