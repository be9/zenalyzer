from __future__ import annotations

import collections
import locale
from dataclasses import dataclass
from typing import DefaultDict, Iterable, Callable, Mapping


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


MultiCurrencySumEvaluator = Callable[[MultiCurrencySum], float]


class ExchangingEvaluator:
    _main_currency: str
    _rates: Mapping[str, float]

    def __init__(self, rates: Mapping[str, float]):
        self._rates = rates

    def __call__(self, mcs: MultiCurrencySum) -> float:
        value = 0.0
        for s in mcs.items():
            value += float(self._rates[s.currency]) * s.sum
        return value


def format_currency(value: float) -> str:
    return locale.currency(value, symbol=False, grouping=True)
