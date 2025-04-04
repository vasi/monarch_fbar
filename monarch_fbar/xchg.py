from csv import DictReader
from datetime import date, timedelta
from io import BytesIO, StringIO
from typing import Dict, Set
from urllib.request import urlopen
import zipfile


class ExchangeRateMissingYear(Exception):
    def __init__(self, year: int):
        super().__init__(f"Exchange rate data from year {year} not yet complete!")


class ExchangeRateMissingCurrency(Exception):
    def __init__(self, currencies: Set[str]):
        cs = ", ".join(sorted(list(currencies)))
        super().__init__(f"Exchange rate data does not include currencies {cs}")


class ExchangeRates(object):
    CACHE = ".mm/exchange_rates.csv"
    URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip"
    DAY = timedelta(days=1)

    EURO = "EUR"
    USD = "USD"

    # date -> currency -> rate-from-euro
    type Data = Dict[date, Dict[str, float]]
    data: Data

    def __parse(self, csvdata: str, year: int, currencies: Set[str]) -> Data:
        reader = self.__reader(csvdata)
        data = {}

        # Save some early data, to fill in missing rows
        first_date = date(year - 1, 12, 1)
        # Want at least one day this late for completion. Spare time for weekends
        target_date = date(year, 12, 28)

        for row in reader:
            dt = date.fromisoformat(row["Date"])
            if dt < first_date or dt.year > year:
                continue

            v = {}
            missing = []
            for c in currencies:
                try:
                    v[c] = float(row[c])
                except ValueError:
                    missing.append(c)
            if missing:
                raise ExchangeRateMissingCurrency(missing)
            data[dt] = v

        # Make sure we have recent data
        if all(d < target_date for d in data.keys()):
            raise ExchangeRateMissingYear(year)

        # Fill in any blanks, and remove data we don't need
        d = first_date
        last = None
        while d.year <= year:
            if cur := data.get(d):
                last = cur
            else:
                data[d] = last
            if d in data:
                del data[d]
            d += self.DAY

        return data

    def __reader(self, csvdata: str):
        return DictReader(StringIO(csvdata))

    def __download(self) -> str:
        with urlopen(self.URL) as f:
            urldata = f.read()
        with zipfile.ZipFile(BytesIO(urldata)) as z:
            names = z.namelist()
            path = zipfile.Path(z, names[0])
            return path.read_text()

    def __init__(self, year: int, currencies: Set[str]):
        csvdata = self.__download()
        currencies = currencies.union({self.USD}) - {self.EURO}
        self.data = self.__parse(csvdata, year, currencies)

    def to_usd(self, d: date, cur: str, amount: float) -> float:
        row = self.data[d]

        if cur == self.EURO:
            eur = amount
        else:
            eur = amount / row[cur]

        return eur * row[self.USD]
