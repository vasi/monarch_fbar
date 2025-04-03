import asyncio

from monarch_fbar import Account, login


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
