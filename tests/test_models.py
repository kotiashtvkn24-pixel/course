from datetime import datetime

import pytest

from app.models import ValidationError, next_year, normalize_username


def test_normalize_username():
    assert normalize_username("  @Taras_K ") == "taras_k"


@pytest.mark.parametrize("value", ["", "ab", "bad name", "1abcde", "@"])
def test_normalize_username_rejects_bad_values(value):
    with pytest.raises(ValidationError):
        normalize_username(value)


def test_next_year_keeps_date_and_time():
    assert next_year(datetime(2026, 11, 10, 9, 30)) == datetime(2027, 11, 10, 9, 30)


def test_next_year_moves_leap_day_to_feb_28():
    assert next_year(datetime(2028, 2, 29, 8, 0)) == datetime(2029, 2, 28, 8, 0)
