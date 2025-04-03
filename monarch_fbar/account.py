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

        result = []
        keys = set(monarch.keys()).union(config.keys())
        for k in keys:
            if a := config.get(k):
                result.append(a)
            else:
                result.append(monarch[k])

        if any(a.currency == cls.CURRENCY_TODO for a in result):
            result.sort()
            cls.__yaml_dump(result)
            return result, True
        else:
            return config_list, False
