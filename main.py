import argparse
import asyncio
import datetime
import logging

from monarch_fbar import Account, ExchangeRates, login

log = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    last_year = datetime.date.today().year - 1
    parser = argparse.ArgumentParser(
        prog="monarch_fbar",
        description="Calculate max account values for FinCEN FBAR from Monarch Money",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--accounts",
        default="accounts.yaml",
        help="Path to YAML file with account configuration",
    )
    parser.add_argument(
        "--year", type=int, default=last_year, help="Tax year to calculate"
    )
    args = parser.parse_args()


async def main():
    args = parse_args()

    mm = await login()
    accounts, incomplete = await Account.load(mm, config_file=args.accounts)
    if incomplete:
        log.warning(
            f"Account currencies incomplete, update {args.accounts}l and re-run."
        )
        return

    currencies = Account.all_currencies(accounts)
    xchg = ExchangeRates(args.year, currencies)


if __name__ == "__main__":
    asyncio.run(main())
