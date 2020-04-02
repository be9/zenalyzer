from collections import defaultdict
from typing import Mapping, DefaultDict, Dict

from zenalyzer.parser import Category
from zenalyzer.sums import Sum, MultiCurrencySum

PerCategorySums = Mapping[Category, MultiCurrencySum]


class TopLevelCategory:
    name: str
    own: MultiCurrencySum
    cumulative: MultiCurrencySum
    subcategories: DefaultDict[str, MultiCurrencySum]

    def __init__(self, name: str):
        self.name = name
        self.own = MultiCurrencySum()
        self.cumulative = MultiCurrencySum()
        self.subcategories = defaultdict(MultiCurrencySum)

    def add(self, category: Category, s: Sum) -> None:
        assert 1 <= len(category) <= 2
        assert category[0] == self.name

        self.cumulative.add(s)

        if len(category) == 1:
            self.own.add(s)
        else:
            self.subcategories[category[1]].add(s)


class Tree:
    top_level_categories: Dict[str, TopLevelCategory]

    def __init__(self, sums: PerCategorySums):
        self.top_level_categories = {}

        for cat, ms in sums.items():
            tlc: TopLevelCategory

            if cat[0] in self.top_level_categories:
                tlc = self.top_level_categories[cat[0]]
            else:
                assert len(cat[0]) > 0
                self.top_level_categories[cat[0]] = tlc = TopLevelCategory(cat[0])

            for s in ms.items():
                tlc.add(cat, s)
