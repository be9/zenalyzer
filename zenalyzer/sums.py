from __future__ import annotations
import collections
from dataclasses import dataclass
from typing import DefaultDict


@dataclass
class Sum:
    sum: float
    currency: str

    def negate(self) -> Sum:
        return Sum(-self.sum, self.currency)


class MultiCurrencySum:
    _sums: DefaultDict[str, float]

    def __init__(self) -> None:
        self._sums = collections.defaultdict(float)

    def add(self, s: Sum) -> None:
        self._sums[s.currency] += s.sum

    def __repr__(self) -> str:
        contents = ", ".join(f"{ccy}: {value}" for ccy, value in self._sums.items())
        return f"<MultiCurrencySum {contents}>"

    def __str__(self) -> str:
        value = ", ".join(f"{value:.2f} {ccy}" for ccy, value in self._sums.items())
        return value if value != "" else "0"
