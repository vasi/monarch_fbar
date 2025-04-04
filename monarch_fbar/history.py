from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import List

from monarchmoney import MonarchMoney
from .account import Account
from .xchg import ExchangeRates


@dataclass
class AccountMax(object):
    account: Account
    date: date
    max_local: float
    max_usd: float

    @classmethod
    def report_maxes(
        cls, mm: MonarchMoney, xchg: ExchangeRates, accounts: List[Account]
    ) -> List[AccountMax]:
        pass

    def report(self):
        pass
