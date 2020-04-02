import argparse
import collections
import datetime
from typing import Mapping, Sequence, DefaultDict, List, Dict

import zenalyzer.parser as parser
from zenalyzer.sums import MultiCurrencySum
from zenalyzer.tree import Tree, mega_table


def make_tree(transactions: Sequence[parser.Transaction]) -> Tree:
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
                expenses[c].add(txn.incoming_sum.negate())

    return Tree(expenses)


def main() -> None:
    argparser = argparse.ArgumentParser(description='Process ZenMoney exports')
    argparser.add_argument('files', metavar='FILE', type=str, nargs='+', help='Source file')
    argparser.add_argument("-m", "--monthly", help="show per-month stats", action="store_true")
    argparser.add_argument("-s", "--start-date", help="start date (YYYY-MM-DD)",
                           required=True, type=_valid_date)
    argparser.add_argument("-e", "--end-date", help="end date (YYYY-MM-DD",
                           required=True, type=_valid_date)
    args = argparser.parse_args()

    all_transactions = []

    for fn in args.files:
        for txn in parser.parse_csv(fn):
            if args.start_date and txn.date < args.start_date:
                continue
            if args.end_date and txn.date > args.end_date:
                continue

            all_transactions.append(txn)

    if args.monthly:
        transactions_by_month: DefaultDict[str, List[parser.Transaction]] = collections.defaultdict(list)
        for txn in all_transactions:
            month = txn.date.strftime("%Y-%m")
            transactions_by_month[month].append(txn)

        trees_by_month: Dict[str, Tree] = {}
        for month, transactions in transactions_by_month.items():
            trees_by_month[month] = make_tree(transactions)

        print(mega_table(trees_by_month).draw())
    else:
        print(make_tree(all_transactions).tableize().draw())


def _valid_date(s) -> datetime.date:
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


if __name__== "__main__":
    main()
