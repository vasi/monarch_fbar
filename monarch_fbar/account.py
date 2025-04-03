from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import yaml
from monarchmoney import MonarchMoney


@dataclass(order=True)
class Account(yaml.YAMLObject):
    CONFIG = "accounts.yaml"

    # User has yet to define how to handle this account
    CURRENCY_TODO = "TODO"
    # User requests skipping this account
    CURRENCY_SKIP = "SKIP"

    INSTITUTION_UNKNOWN = "UNKNOWN"

    # Order by institution, it's easiest to add to FBAR
    institution: str
    name: str
    id: str
    currency: str

    yaml_loader = yaml.SafeLoader
    yaml_dumper = yaml.SafeDumper
    yaml_tag = "tag:yaml.org,2002:map"

    def needs_editing(self) -> bool:
        return self.currency.upper() == self.CURRENCY_TODO

    def skip(self) -> bool:
        return self.currency.upper() == self.CURRENCY_SKIP

    @classmethod
    async def __fetch_from_monarch(cls, mm: MonarchMoney) -> List[Account]:
        data = await mm.get_accounts()
        accounts = []
        for a in data["accounts"]:
            if not a["isAsset"]:
                continue

            institution = (a["institution"] or {}).get("name", cls.INSTITUTION_UNKNOWN)
            account = cls(
                id=a["id"],
                institution=institution,
                name=a["displayName"],
                currency=cls.CURRENCY_TODO,
            )
            accounts.append(account)
        return accounts

    @classmethod
    def __yaml_dump(cls, accounts: List[Account]):
        with open(cls.CONFIG, "w") as f:
            yaml.safe_dump(accounts, f, sort_keys=False)

    @classmethod
    def __yaml_load(cls) -> List[Account]:
        try:
            with open(cls.CONFIG) as f:
                return yaml.safe_load(f)

        except FileNotFoundError:
            return []

    @classmethod
    async def load_merged(cls, mm: MonarchMoney) -> tuple[List[Account], bool]:
        """Returns true in config needs editing"""
        monarch_list = await cls.__fetch_from_monarch(mm)
        monarch = {a.id: a for a in monarch_list}

        config_list = cls.__yaml_load()
        config = {a.id: a for a in config_list}

        new_list = []
        keys = set(monarch.keys()).union(config.keys())
        for k in keys:
            if a := config.get(k):
                new_list.append(a)
            else:
                new_list.append(monarch[k])

        if any(a.needs_editing() for a in new_list):
            new_list.sort()
            cls.__yaml_dump(new_list)
            return new_list, True
        else:
            result = [a for a in config_list if not a.skip()]
            return result, False
