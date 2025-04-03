import asyncio
import logging

import argparse
from monarch_fbar import Account, login

log = logging.getLogger(__name__)


async def main():
    parser = argparse.ArgumentParser(prog="monarch_fbar")
    parser.add_argument("--accounts", default="accounts.yaml")
    args = parser.parse_args()

    mm = await login()
    accounts, incomplete = await Account.load(mm, config_file=args.accounts)
    if incomplete:
        log.warning(
            f"Account currencies incomplete, update {args.accounts}l and re-run."
        )
        return

    currencies = Account.all_currencies(accounts)
    print(currencies)


if __name__ == "__main__":
    asyncio.run(main())
