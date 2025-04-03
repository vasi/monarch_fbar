from __future__ import annotations
from enum import auto, StrEnum
from typing import Any, List, IO, Optional, NewType, Union

import asyncio
from gql.transport.exceptions import TransportServerError
from monarchmoney import MonarchMoney, LoginFailedException
import yaml


class CurrencySpecial(StrEnum):
    TODO = auto()
    SKIP = auto()


CurrencyCode = NewType("Currency", str)
Currency = Union[CurrencyCode, CurrencySpecial]


class Account(yaml.YAMLObject):
    yaml_loader = yaml.SafeLoader
    yaml_dumper = yaml.SafeDumper
    yaml_tag = "tag:yaml.org,2002:map"

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
        # TODO: sort
        return accounts

    def __repr__(self) -> str:
        return f"<Account {self.name!r} {self.institution!r} {self.id} {self.currency}>"

    @classmethod
    def to_yaml(cls, dumper: yaml.Dumper, data: Account) -> Any:
        return dumper.represent_mapping(
            cls.yaml_tag,
            {
                "id": data.id,
                "institution": data.institution,
                "name": data.name,
                "currency": str(data.currency),
            },
        )

    @classmethod
    def yaml_dump(cls, stream: IO, accounts: List[Account]):
        yaml.safe_dump(accounts, stream, sort_keys=False)

    @classmethod
    def yaml_load(cls, stream: IO) -> List[Account]:
        return yaml.load(stream, Loader=yaml.SafeLoader)


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
    from_monarch = await Account.fetch_from_monarch(mm)
    with open("accounts.yaml", "w") as f:
        Account.yaml_dump(f, from_monarch)
    with open("accounts.yaml") as f:
        from_yaml = Account.yaml_load(f)
    for a in from_yaml:
        print(a)


if __name__ == "__main__":
    asyncio.run(main())
