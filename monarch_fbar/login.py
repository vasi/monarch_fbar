from typing import Dict, Optional

import getpass
from monarchmoney import MonarchMoney, RequireMFAException
import yaml


async def login_with_session(mm: MonarchMoney, creds: Dict[str, str]):
    await mm.login(**creds)


async def login_without_session(mm: MonarchMoney, creds: Dict[str, str]):
    await mm.login(**creds, use_saved_session=False)


async def login_interactive(mm: MonarchMoney, creds: Dict[str, str]):
    email = input("Email: ")
    passwd = getpass.getpass("Password: ")
    try:
        await mm.login(email, passwd, use_saved_session=False)
    except RequireMFAException:
        mfa = input("MFA code: ")
        await mm.multi_factor_authenticate(email, passwd, mfa)
        mm.save_session()


async def login(creds_file: Optional[str]) -> MonarchMoney:
    creds = {}
    if creds_file:
        with open(creds_file, "r") as f:
            creds = yaml.safe_load(f)

    attempts = [login_with_session, login_without_session, login_interactive]
    last_exception = None
    for attempt in attempts:
        try:
            mm = MonarchMoney()
            await attempt(mm, creds)
            await mm.get_accounts()  # test that we're authenticated
            return mm
        except Exception as e:
            last_exception = e
    raise last_exception
