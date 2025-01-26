# Tarsnap - tarsnap website interface

import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup, element

URL = "https://www.tarsnap.com"


class Tarsnap:
    def __init__(self, config_file, account=None, email=None, password=None):

        self.url = URL
        self.account = account or "undefined"
        self.config = {}
        if config_file and config_file.exists():
            for line in Path(config_file).open("r").readlines():
                _account, _email, _password = line.split()
                self.config[_account] = dict(email=_email, password=_password)
                if not account:
                    account = _account

        _config = self.config.get(account, {})

        self.email = email or _config.get("email")
        self.password = password or _config.get("password")

        self.session = requests.Session()

    def _post(self, route, data):
        return self.session.post(self.url + "/" + route, data)

    def _get(self, route):
        return self.session.get(self.url + "/" + route)

    def _round(self, value):
        return float("%.2f" % value)

    def _query(self):

        response = self._post(
            "manage.cgi", {"address": self.email, "password": self.password}
        )

        # for div in [soup.find('div')]:
        #   print('div: %s ' % repr(div.text))

        balance = None
        account = None
        verbose_soup = None

        soup = BeautifulSoup(response.text, "html.parser")
        # print(soup.prettify())

        for el in [
            e for e in soup.find_all("div") if e and isinstance(e, element.Tag)
        ]:
            for div in [
                e
                for e in el.find_all("div")
                if e and isinstance(e, element.Tag)
            ]:
                if div.attrs.get("class") == ["boxcontents"]:
                    msg = div.text.strip().split("\n")[0]
                    if f"You are logged in as {self.email}" not in msg:
                        raise RuntimeError(msg)

        for el in soup.find("div").find_all("p"):
            if "current account balance" in el.text:
                balance = self._round(float(el.find("code").text[1:]))
            elif "logged in as" in el.text:
                account = el.find("code").text

        for el in soup.find_all("a", href=True):
            if el["href"].endswith("verboseactivity"):
                response = self._get(el["href"])
                verbose_soup = BeautifulSoup(response.text, "html.parser")
                break

        return balance, account, verbose_soup

    def _handle_row(self, r, row):
        if row[0] == "Balance":
            r["balances"].append((row[1], float(row[6])))
        if row[0] == "Payment":
            payment = float(row[5])
            r["payments"][row[1]] = payment
        else:
            payment = 0
        return payment

    def get_status(
        self,
        rows=False,
        balances=False,
        payments=False,
        raw=False,
        email=None,
        password=None,
    ):

        email = email or self.email
        password = password or self.password

        if not email:
            raise ValueError("--email is required")

        if not password:
            raise ValueError("--password is required")

        balance, account, soup = self._query()
        r = {}
        r["balance"] = balance
        r["account"] = account
        r["rows"] = []
        r["balances"] = []
        r["payments"] = {}
        payment_total = 0.0

        for el in soup.find("table").find_all("tr"):
            r["rows"].append([el.text for el in el.find_all("td")])

        for row in r["rows"]:
            payment_total += self._handle_row(r, row)

        if not raw:
            if r["balances"]:
                begin_date = datetime.datetime.strptime(
                    r["balances"][0][0], "%Y-%m-%d"
                )
                begin_amount = float(r["balances"][0][1])
                end_date = datetime.datetime.strptime(
                    r["balances"][-1][0], "%Y-%m-%d"
                )
                end_amount = float(r["balances"][-1][1])
                r["monthly_cost"] = self._round(
                    (begin_amount - (end_amount - payment_total))
                    / (end_date - begin_date).days
                    * 365
                    / 12
                )

        if not rows:
            del r["rows"]

        if not balances:
            del r["balances"]

        if not payments:
            del r["payments"]

        return r
