import asyncio
import json

from gql.transport.exceptions import TransportServerError
from monarchmoney import MonarchMoney, LoginFailedException


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
    accounts = await mm.get_accounts()
    print(json.dumps(accounts, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
