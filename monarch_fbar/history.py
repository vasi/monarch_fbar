from __future__ import annotations
import asyncio
from dataclasses import dataclass
from datetime import date
from math import inf
from typing import Dict, List

from monarchmoney import MonarchMoney
from tabulate import tabulate
from .account import Account
from .xchg import ExchangeRates


@dataclass
class AccountMax(object):
    account: Account
    date_at_max: date
    local_at_max: float
    max_usd: float


@dataclass
class History(object):
    mm: MonarchMoney
    xchg: ExchangeRates
    year: int
    accounts: List[Account]

    async def __get_balances(self, account: Account) -> Dict[date, float]:
        raw = await self.mm.get_account_history(account.id)
        results = {}
        for h in raw:
            d = date.fromisoformat(h["date"])
            if d.year != self.year:
                continue
            balance = float(h["signedBalance"])
            results[d] = balance
        return results

    async def __find_max(self, account: Account) -> AccountMax:
        balances = await self.__get_balances(account)

        max_usd = -inf
        date_at_max = None
        local_at_max = None

        for d, local in balances.items():
            usd = self.xchg.to_usd(d, account.currency_symbol(), local)
            if usd > max_usd:
                max_usd = usd
                date_at_max = d
                local_at_max = local
        return AccountMax(account, date_at_max, local_at_max, max_usd)

    @classmethod
    async def maxes(
        cls, mm: MonarchMoney, xchg: ExchangeRates, year: int, accounts: List[Account]
    ) -> List[AccountMax]:
        h = History(mm, xchg, year, accounts)
        tasks = [h.__find_max(a) for a in accounts]
        return await asyncio.gather(*tasks)

    @classmethod
    def print_table(cls, maxes: List[AccountMax]):
        headers = ["Institution", "Account", "Date", "Max USD", "Local"]
        table = []
        for max in maxes:
            if max.max_usd <= 0:
                continue
            table.append(
                [
                    max.account.institution,
                    max.account.name,
                    max.date_at_max.isoformat(),
                    max.max_usd,
                    max.local_at_max,
                ]
            )
        print(tabulate(table, headers=headers, floatfmt=".2f"))
