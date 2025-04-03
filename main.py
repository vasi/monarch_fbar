import asyncio
import logging

from monarch_fbar import Account, login

log = logging.getLogger(__name__)


async def main():
    mm = await login()
    accounts, incomplete = await Account.load_merged(mm)
    if incomplete:
        log.warning("Account currencies incomplete, update accounts.yaml and re-run.")
        return


if __name__ == "__main__":
    asyncio.run(main())
