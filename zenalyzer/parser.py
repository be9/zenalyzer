import csv
import datetime
import enum
import typing
from dataclasses import dataclass

from zenalyzer.sums import Sum

Category = typing.Sequence[str]


class TransactionType(enum.Enum):
    INCOME = 1
    OUTGOING = 2
    TRANSFER = 3


@dataclass
class Transaction:
    date: datetime.date
    category: str
    payee: str
    comment: str

    outgoing_account: typing.Optional[str]
    outgoing_sum: typing.Optional[Sum]

    incoming_account: typing.Optional[str]
    incoming_sum: typing.Optional[Sum]

    def primary_category(self) -> typing.Optional[Category]:
        cats = self.category.split(', ')
        if len(cats) < 1:
            return None

        cat = cats[0].split(' / ')
        assert 1 <= len(cat) <= 2
        if cat[0] == "":
            cat[0] = "UNCATEGORIZED"

        return tuple(cat)

    def type(self) -> TransactionType:
        if self.outgoing_account and self.outgoing_sum:
            if self.incoming_account and self.incoming_sum:
                return TransactionType.TRANSFER
            else:
                return TransactionType.OUTGOING
        else:
            assert self.incoming_account
            assert self.incoming_sum
            return TransactionType.INCOME


def parse_csv(filename) -> typing.Iterable[Transaction]:
    with open(filename, "r") as csvfile:
        rdr = csv.reader(csvfile)

        header = True

        for row in rdr:
            if header:
                if len(row) > 0 and row[0] == 'date':
                    header = False
                continue

            date = datetime.datetime.strptime(row[0], '%Y-%m-%d').date()
            outgoing_acc = row[4] if row[4] != '' else None
            incoming_acc = row[7] if row[7] != '' else None

            t = Transaction(date=date, category=row[1], payee=row[2], comment=row[3],
                            outgoing_account=outgoing_acc, outgoing_sum=_parse_sum(row[5], row[6]),
                            incoming_account=incoming_acc, incoming_sum=_parse_sum(row[8], row[9]))
            # print(row)
            # print(t.type(), t.primary_category(), t)
            yield t


def _parse_sum(s: str, currency: str) -> typing.Optional[Sum]:
    if s == '' or currency == '':
        return None

    return Sum(sum=float(s.replace(',', '.')), currency=currency)
