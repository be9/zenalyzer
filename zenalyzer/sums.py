from __future__ import annotations

import collections
from dataclasses import dataclass
from typing import DefaultDict, Iterable


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

    def nonzero(self) -> bool:
        return len(self._sums) > 0

    def add(self, s: Sum) -> None:
        self._sums[s.currency] += s.sum

    def items(self) -> Iterable[Sum]:
        for ccy, s in self._sums.items():
            yield Sum(s, ccy)

    def __repr__(self) -> str:
        contents = ", ".join(f"{ccy}: {value}" for ccy, value in self._sums.items())
        return f"<MultiCurrencySum {contents}>"

    def __str__(self) -> str:
        value = ", ".join(f"{value:.2f} {ccy}" for ccy, value in self._sums.items())
        return value if value != "" else "0"

    def format_multiline(self) -> str:
        value = " +\n".join(f"{value:.2f} {ccy}" for ccy, value in self._sums.items())
        return value
