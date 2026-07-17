# tools/currency.py

import requests

from config import CURRENCY_API_KEY



def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
) -> dict:

    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    if from_currency == to_currency:
        return {
            "amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "converted_amount": round(amount, 2),
            "exchange_rate": 1.0,
        }

    params = {
        "apikey": CURRENCY_API_KEY,
        "base_currency": from_currency,
        "currencies": to_currency,
    }

    response = requests.get(
        "https://api.currencyapi.com/v3/latest",
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    rate = data["data"][to_currency]["value"]

    return {
        "amount": amount,
        "from_currency": from_currency,
        "to_currency": to_currency,
        "exchange_rate": rate,
        "converted_amount": round(amount * rate, 2),
    }