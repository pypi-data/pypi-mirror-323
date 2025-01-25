from contextlib import nullcontext
from decimal import Decimal, InvalidOperation
from typing import Any

import pytest

from percents.percent_type import Percent

NULL_ERROR_CONTEXT = nullcontext()


@pytest.mark.parametrize(
    "value, multiplier, error_context",
    [
        [1, Decimal("0.01"), NULL_ERROR_CONTEXT],
        ["20", Decimal("0.2"), NULL_ERROR_CONTEXT],
        [50.0, Decimal("0.5"), NULL_ERROR_CONTEXT],
        [Decimal("30"), Decimal("0.3"), NULL_ERROR_CONTEXT],
        ["abc", None, pytest.raises(InvalidOperation)],
        [None, None, pytest.raises(TypeError)],
    ],
)
def test_person_value(value: Any, multiplier: Decimal, error_context: Any) -> None:
    with error_context:
        percent = Percent(value)
    if error_context == NULL_ERROR_CONTEXT:
        assert percent.multiplier == multiplier


def test_percent_math() -> None:
    assert 10 + Percent(50) == 15
    assert 10 - Percent(50) == 5

    result = 10.0 + Percent(50)
    assert result == 15.0
    assert type(result) == float


def test_percent_ordering() -> None:
    percent1 = Percent(10)
    percent2 = Percent(20)
    assert percent2 != percent1
    assert percent2 > percent1
    assert percent1 < percent2

    percent1 = Percent(10)
    percent2 = Percent(10)
    assert percent2 == percent1
    assert percent2 >= percent1
    assert percent1 <= percent2

    percent = Percent(10)
    assert percent == 10
    assert percent != 11
    assert percent > 9
    assert percent < 11
    assert percent >= 10.0
    assert percent <= 10.0
