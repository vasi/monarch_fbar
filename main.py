import argparse
import asyncio
import datetime
import logging

from monarch_fbar import Account, ExchangeRates, login, report_maxes

log = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    last_year = datetime.date.today().year - 1
    parser = argparse.ArgumentParser(
        prog="monarch_fbar",
        description="Calculate max account values for FinCEN FBAR from Monarch Money",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--credentials",
        help="Path to YAML file containing credentials for Monarch Money. Valid keys are email, password, mfa_secret_key",
    )
    parser.add_argument(
        "--accounts",
        default="accounts.yaml",
        help="Path to YAML file with account configuration",
    )
    parser.add_argument(
        "--year", type=int, default=last_year, help="Tax year to calculate"
    )
    return parser.parse_args()


async def main():
    try:
        args = parse_args()

        mm = await login(args.credentials)
        accounts = await Account.load(mm, config_file=args.accounts)

        currencies = Account.all_currencies(accounts)
        xchg = ExchangeRates(args.year, currencies)

        maxes = report_maxes(mm, xchg, accounts)

    except Exception as e:
        if not e.__class__.__module__.startswith("monarch_fbar"):
            raise e  # unexpected!
        log.critical(e)
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
