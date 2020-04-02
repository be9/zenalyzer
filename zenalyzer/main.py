import argparse
import collections
from typing import Mapping

from texttable import Texttable

import zenalyzer.parser as parser
from zenalyzer.sums import MultiCurrencySum
from zenalyzer.tree import Tree

argparser = argparse.ArgumentParser(description='Process ZenMoney exports')
argparser.add_argument('files', metavar='FILE', type=str, nargs='+', help='Source file')

transactions = []

for fn in argparser.parse_args().files:
    for txn in parser.parse_csv(fn):
        transactions.append(txn)

outgoing = [
    txn
    for txn in transactions
    if txn.type() == parser.TransactionType.OUTGOING
]

expenses: Mapping[parser.Category, MultiCurrencySum] = \
    collections.defaultdict(MultiCurrencySum)

for txn in outgoing:
    c = txn.primary_category()
    assert c
    assert 1 <= len(c) <= 2
    assert txn.outgoing_sum
    expenses[c].add(txn.outgoing_sum)

cats = set(expenses.keys())

for txn in transactions:
    if txn.type() == parser.TransactionType.INCOME:
        c = txn.primary_category()
        assert c
        if c in cats:
            assert txn.incoming_sum
            # print(txn)
            expenses[c].add(txn.incoming_sum.negate())

# print(expenses)
# print(cats)

tree = Tree(expenses)
# print(tree)

table = Texttable()
table.set_deco(Texttable.HEADER)
table.set_cols_dtype(['t', 't', 'f'])

table.header(['Category', 'Subcategory', 'Sum'])
table.set_max_width(0)

for tlc in sorted(tree.top_level_categories.values(), key=lambda tlc: tlc.name):
    table.add_row([
        tlc.name,
        '',
        str(tlc.cumulative),
    ])

    if tlc.own.nonzero():
        table.add_row([
            '',
            '___',
            str(tlc.own),
        ])

    for subcat in sorted(tlc.subcategories):
        msc = tlc.subcategories[subcat]
        table.add_row([
            '',
            subcat,
            str(msc),
        ])

print(table.draw())