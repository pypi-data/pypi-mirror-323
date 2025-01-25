from decimal import Decimal
from functools import total_ordering
from typing import Any, TypeVar

T = TypeVar("T", bound=Any)


@total_ordering
class Percent:
    def __init__(self, value: int | float | Decimal | str) -> None:
        self.value = Decimal(value)
        self.multiplier = Decimal(value) / Decimal(100)

    def __str__(self) -> str:
        return f"{self.value}%"

    def __bool__(self) -> bool:
        return bool(self.multiplier)

    def __radd__(self, other: T) -> T:
        if not isinstance(other, (int | float | Decimal | str)):
            return NotImplemented

        decimal_other = Decimal(other)
        other_type = type(other)
        result = decimal_other + decimal_other * self.multiplier
        return other_type(result)  # type: ignore

    def __rsub__(self, other: T) -> T:
        if not isinstance(other, (int | float | Decimal | str)):
            return NotImplemented

        decimal_other = Decimal(other)
        result = decimal_other - decimal_other * self.multiplier
        other_type = type(other)
        return other_type(result)  # type: ignore

    def __rmul__(self, other: T) -> T:
        if not isinstance(other, (int | float | Decimal | str)):
            return NotImplemented

        decimal_other = Decimal(other)
        result = decimal_other * self.multiplier
        other_type = type(other)
        return other_type(result)  # type: ignore

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Percent):
            return self.value == other.value
        if isinstance(other, (int | float | Decimal)):
            return self.value == other
        return NotImplemented

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, Percent):
            return self.value < other.value
        if isinstance(other, (int | float | Decimal)):
            return self.value < other
        return NotImplemented
