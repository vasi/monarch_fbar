from __future__ import annotations
from enum import auto, StrEnum
from typing import Any, List, Optional, NewType, Union

import asyncio

from gql.transport.exceptions import TransportServerError
from monarchmoney import MonarchMoney, LoginFailedException


class CurrencySpecial(StrEnum):
    TODO = auto()
    SKIP = auto()


CurrencyCode = NewType("Currency", str)
Currency = Union[CurrencyCode, CurrencySpecial]


class Account(object):
    __EXCLUDED_TYPES = {"credit", "loan", "other_asset"}

    id: str
    institution: Optional[str]
    name: str
    currency: Currency

    def __init__(
        self, id: str, institution: Optional[str], name: str, currency: Currency
    ):
        self.id = id
        self.institution = institution
        self.name = name
        self.currency = currency

    @classmethod
    async def fetch_from_monarch(cls, mm: MonarchMoney) -> List[Account]:
        data = await mm.get_accounts()
        accounts = []
        for a in data["accounts"]:
            account_type = a["type"]["name"]
            if account_type in cls.__EXCLUDED_TYPES:
                continue
            account = cls(
                id=a["id"],
                institution=(a["institution"] or {}).get("name"),
                name=a["displayName"],
                currency=CurrencySpecial.TODO,
            )
            accounts.append(account)
        return accounts

    def __repr__(self) -> str:
        return f"<Account {self.name!r} {self.institution!r} {self.id} {self.currency}>"


async def redo_login() -> MonarchMoney:
    mm = MonarchMoney()
    await mm.interactive_login(use_saved_session=False)
    return mm


async def login() -> MonarchMoney:
    mm = MonarchMoney()
    try:
        await mm.login()
        await mm.get_accounts()  # test that we're authenticated
        return mm
    except LoginFailedException:
        return await redo_login()
    except TransportServerError as e:
        if e.code != 401:
            raise e
        return await redo_login()


async def main():
    mm = await login()
    accounts = await Account.fetch_from_monarch(mm)
    for a in accounts:
        print(a)


if __name__ == "__main__":
    asyncio.run(main())
