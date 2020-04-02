import argparse
import collections
from typing import Mapping

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

tree = Tree(expenses)
print(tree.tableize().draw())