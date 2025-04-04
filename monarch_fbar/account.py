from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List, Optional, Set

import yaml
from monarchmoney import MonarchMoney


class AccountsNeedEditing(Exception):
    def __init__(self, config_file: str):
        super().__init__(
            f"Account currencies incomplete, update {config_file} and re-run"
        )


@dataclass(order=True)
class Account(yaml.YAMLObject):
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
    yaml_tag = "!account"

    def needs_editing(self) -> bool:
        return self.currency.upper() == self.CURRENCY_TODO

    def skip(self) -> bool:
        return self.currency.upper() == self.CURRENCY_SKIP

    def currency_symbol(self) -> Optional[str]:
        if self.skip() or self.needs_editing():
            return None
        return self.currency.upper()

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
    def __yaml_dump(cls, config: str, accounts: List[Account]):
        with open(config, "w") as f:
            yaml.safe_dump(accounts, f, sort_keys=False)

    @classmethod
    def __yaml_load(cls, config: str) -> List[Account]:
        try:
            with open(config) as f:
                return yaml.safe_load(f)

        except FileNotFoundError:
            return []

    @classmethod
    async def load(cls, mm: MonarchMoney, config_file: Optional[str]) -> List[Account]:
        monarch_list = await cls.__fetch_from_monarch(mm)

        config_list = cls.__yaml_load(config_file)
        config_ids = {a.id for a in config_list}

        # See if anything new needs adding to the list
        new_list = config_list.copy()
        for a in monarch_list:
            if not a.id in config_ids:
                new_list.append(a)
        if any(a.needs_editing() for a in new_list):
            if not config_list:
                # only sort if all new, otherwise respect user sorting
                new_list.sort()
            cls.__yaml_dump(config_file, new_list)
            raise AccountsNeedEditing(config_file)

        return [a for a in config_list if not a.skip()]

    @classmethod
    def all_currencies(cls, accounts: List[Account]) -> Set[str]:
        return {a.currency_symbol() for a in accounts}
