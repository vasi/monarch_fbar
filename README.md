# monarch_fbar

Find [US FBAR](https://bsaefiling.fincen.treas.gov/NoRegFBARFiler.html) form amounts using [Monarch Money](https://www.monarchmoney.com/).

## What this is for

"US persons" with substancial financial assets outside the US are required to file special forms every year:

- IRS Form 8938 Statement of Specified Foreign Financial Assets
- FinCEN Form 114 Report of Foreign Bank and Financial Accounts (FBAR)

This applies to millions of regular people who happen to be US citizens but live, work and bank in other countries; as well as immigrants in the US who still have bank accounts in their country of origin.

Unfortunately, these forms require the **maximum value of each account over in US dollars** over the year in question. **Who knows that kind of thing!?**

But if you're using Monarch Money to track your finances, this tool makes it much easier to figure out your 8938/FBAR amounts.

**WARNING**: I am not your accountant or lawyer, and I make no guarantees as to the correctness of any data output by this tool. You are responsible for your own financial reporting.

## Usage

1. Make sure you're using [Monarch Money](https://www.monarchmoney.com/), and that all accounts you care about are tracked there.
2. Make sure you've enabled MFA (Multi-Factor Authentication) in your Monarch Money account. You can set this up in the "Security" page in Monarch's settings. You may want to save the MFA "seed" value that Monarch provides.
3. Clone this repo using git: `git clone https://github.com/vasi/monarch_fbar.git; cd monarch_fbar`
4. Get the [UV package manager](https://docs.astral.sh/uv/getting-started/installation/), if you don't already have it: `curl -LsSf https://astral.sh/uv/install.sh | sh`
5. Run the script a first time: `uv run main.py`. This will ask for your Monarch Money credentials, and then output a file `accounts.yaml` listing your accounts.
6. Edit accounts.yaml. Since Monarch doesn't track the currency of each account, they'll all show `currency: TODO`. Change "TODO" to either:

   - A [currency code](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html), such as "USD", "CAD", "JPY", etc
   - The string "skip", to indicate that you're not interested in this account. For example, maybe it's based in the US, so doesn't need to be reported.

   You may also give the accounts different names, or reorder them. Just don't change the "id" field.

7. Run the script again: `uv run main.py`. This will output a table with the max USD value of each account over the previous calendar year. The "Max USD" field corresponds to the maximum USD value of that account over the year in question. Eg:

```
Institution    Account      Date          Max USD       Local
-------------  -----------  ----------  ---------  ----------
Barclays       Checking     2024-09-16    1234.56     1234.56
Mizuho         Savings      2024-09-29     789.01   234567.89
```

8. Double check any values returned by this tool before using them in any government forms. Remember, I am not your accountant, and you are responsible for your own reporting.

## Options

There are several supported options. Most interesting are:

- `--year` selects the calendar year you're interested in
- `--credentials` allows storing your Monarch Money credentials in a file, so they're not constantly expiring. The file should look like:

  ```
  email: me@example.com
  password: abc123
  mfa_secret_key: Z5W3T4X8E2SFUA2NHJHWYRYAF919ORD0
  ```

  The mfa_secret_key is the MFA "seed" that Monarch Money gives you when you setup MFA.

## License

This software is (C) 2025 Dave Vasilevsky, available under the MIT License.
