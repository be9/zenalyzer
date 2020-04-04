from collections import defaultdict
from typing import Mapping, DefaultDict, Dict, Set

from texttable import Texttable

from zenalyzer.parser import Category
from zenalyzer.sums import Sum, MultiCurrencySum, MultiCurrencySumFormatter

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

    def tableize(self, fmt: MultiCurrencySumFormatter) -> Texttable:
        table = _new_table()
        table.set_cols_dtype(['t', 't', 'f'])
        table.header(['Category', 'Subcategory', 'Sum'])

        for tlc in sorted(self.top_level_categories.values(), key=lambda _tlc: _tlc.name):
            table.add_row([
                tlc.name,
                '',
                fmt(tlc.cumulative),
            ])

            if tlc.own.nonzero() and len(tlc.subcategories) > 0:
                table.add_row([
                    '',
                    '___',
                    fmt(tlc.own),
                ])

            for subcat in sorted(tlc.subcategories):
                msc = tlc.subcategories[subcat]
                table.add_row([
                    '',
                    subcat,
                    fmt(msc),
                ])

        return table


def mega_table(trees_dict: Mapping[str, Tree], fmt: MultiCurrencySumFormatter) -> Texttable:
    table = _new_table()
    table.set_cols_dtype(['t', 't'] + ['t'] * len(trees_dict))

    labels = sorted(trees_dict)
    table.header(['Category', 'Subcategory'] + labels)

    all_top_level: Set[str] = set()

    trees = [trees_dict[k] for k in labels]
    for tree in trees:
        for tlc in tree.top_level_categories.values():
            all_top_level.add(tlc.name)

    for top_level_name in sorted(all_top_level):
        top_row = [top_level_name, '']
        top_own_row = ['', '___']
        all_subcats: Set[str] = set()

        # 2 top-level rows
        has_own = False
        has_subcats = False

        for tree in trees:
            if top_level_name in tree.top_level_categories:
                tlc = tree.top_level_categories[top_level_name]
                top_row.append(fmt(tlc.cumulative))
                top_own_row.append(fmt(tlc.own))
                if tlc.own.nonzero():
                    has_own = True

                for subcat in tlc.subcategories.keys():
                    has_subcats = True
                    all_subcats.add(subcat)
            else:
                top_row.append('')
                top_own_row.append('')

        table.add_row(top_row)
        if has_own and has_subcats:
            table.add_row(top_own_row)

        # Subcategories
        for subcat in sorted(all_subcats):
            subcat_row = ['', subcat]

            for tree in trees:
                value = ''
                if top_level_name in tree.top_level_categories:
                    tlc = tree.top_level_categories[top_level_name]
                    if subcat in tlc.subcategories:
                        value = fmt(tlc.subcategories[subcat])

                subcat_row.append(value)

            table.add_row(subcat_row)

    return table


def _new_table() -> Texttable:
    table = Texttable()
    table.set_deco(Texttable.HEADER)
    table.set_max_width(0)
    return table
