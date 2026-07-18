#mcp_server_sse.py

from datetime import datetime

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------
# Business logic
# ---------------------------------------------------------------------

from tools.flights import search_flights as _search_flights
from tools.hotels import search_hotels as _search_hotels
from tools.weather import fetch_weather as _fetch_weather
from tools.sightseeing import fetch_sightseeing as _fetch_sightseeing
from tools.currency import convert_currency as _convert_currency


# Import calendar tools
from tools.calendar_core import get_current_datetime as _get_current_datetime
from tools.calendar_core import get_reference_calendar as _get_reference_calendar


mcp = FastMCP("Travel MCP")


# =====================================================================
# Flights
# =====================================================================

@mcp.tool()
def search_flights(
    origin: str,
    destination: str,
    start_date: str,
    end_date: str | None = None,
    currency: str = "USD",
    adults: int = 1,
    travel_class: str = "ECONOMY",
) -> dict:
    """
    Search flights using Google Flights.

    Arguments
    ---------
    origin
        Three-letter IATA airport code.
    destination
        Three-letter IATA airport code.
    start_date
        Departure date in YYYY-MM-DD format.
    end_date
        return date in YYYY-MM-DD format.
    currency
        Currency code (USD, INR, EUR, etc.)

    adults
        Number of adult passengers.
    travel_class
        Cabin class.

        One of:
        - ECONOMY
        - PREMIUM_ECONOMY
        - BUSINESS
        - FIRST


    Returns
    -------
    Dictionary containing:

    - best_flights
    - other_flights

    Each flight includes:

    - price
    - duration
    - carbon emissions
    - layovers
    - flight legs
    """

    print("Flight tool invoked")

    return _search_flights(
        origin=origin,
        destination=destination,
        start_date=start_date,
        end_date=end_date,
        currency=currency,
        adults=adults,
        travel_class=travel_class,
    )

# =====================================================================
# Hotels
# =====================================================================

@mcp.tool()
def search_hotels(
    location: str,
    check_in_date: str,
    check_out_date: str,
    adults: int = 2,
) -> list:
    """
    Search hotels.

    Arguments
    ---------
    location
        Any geographic location supported by the hotel provider.

        Examples

        - Paris
        - Santorini
        - Tuscany
        - Greece
        - Bali

    check_in_date
        YYYY-MM-DD

    check_out_date
        YYYY-MM-DD

    adults
        Number of adults.

    Returns
    -------
    Hotel name

    Price

    Rating

    Address

     Booking link
    """
    print("Hotel tool invoked")
    return _search_hotels(
        location,
        check_in_date,
        check_out_date,
        adults,
    )


# =====================================================================
# Weather
# =====================================================================

@mcp.tool()
def fetch_weather(
    location: str,
    start_date: str,
    end_date: str,
) -> dict:
    """
    Retrieve weather forecasts.

    Arguments
    ---------
    location

        Any supported geographic location.

        Examples

        - city
        - country
        - island
        - state
        - region
        - village

    start_date
        YYYY-MM-DD

    end_date
        YYYY-MM-DD

    Returns
    -------
    Daily forecast containing 3-hour weather readings.
    """
    print("weather tool invoked")
    return _fetch_weather(
        location,
        start_date,
        end_date,
    )


# =====================================================================
# Sightseeing
# =====================================================================

@mcp.tool()
def fetch_sightseeing(
    location: str,
) -> list:
    """
    Search tourist attractions.

    Arguments
    ---------
    location

        Any geographic location.

        Examples

        - Paris
        - Greece
        - Santorini
        - Tuscany
        - California
        - Portofino

    Behaviour
    ---------
    • Call this tool once for every location mentioned by the user.

    • Pass the location exactly as understood from the user's request.

    Returns
    -------
    Name

    Address

    Rating
    """
    print("sightseeing tool invoked")
    return _fetch_sightseeing(location)


# =====================================================================
# Currency
# =====================================================================

@mcp.tool()
def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
) -> dict:
    """
    Convert currency.

    Arguments
    ---------
    amount
        Positive numeric value.

    from_currency
        Three-letter ISO currency code.

    to_currency
        Three-letter ISO currency code.

    Examples

        USD

        INR

        EUR

        GBP

        JPY

    Returns
    -------
    Exchange rate

    Converted amount
    """
    print("currency tool invoked")
    return _convert_currency(
        amount,
        from_currency,
        to_currency,
    )


# ---------- Calendar tools ----------

@mcp.tool()
def get_current_datetime(tz_name: str = "UTC") -> dict:
    """
    Get the real current date and time in a given timezone.

    **Always call this first** when the user asks about relative dates
    (e.g., "next Friday", "tomorrow", "in two weeks") – do NOT guess
    today's date. The LLM cannot reliably know the current date without
    this tool.

    Args:
        tz_name: IANA timezone name, e.g. "Asia/Kolkata", "America/New_York",
                 "Europe/London". Defaults to "UTC".

    Returns:
        A dictionary with:
            - timezone
            - iso_datetime (full ISO string)
            - date (YYYY-MM-DD)
            - time_24h
            - weekday_name (e.g., "Tuesday")
            - day, month, month_name, year
    """
    result = _get_current_datetime(tz_name)
    return result.model_dump()


@mcp.tool()
def get_reference_calendar(
    year: int,
    month: int,
    first_weekday: str = "Monday",
    today_override: str | None = None,
) -> dict:
    """
    Return a full calendar grid for a given month and year.

    Use this tool to:
    - See which day of the week a date falls on.
    - Count weekends or specific weekdays.
    - Navigate relative dates like "the second Saturday of August" or
      "last weekday of the month".

    The grid shows each week as a row, with each day's date, weekday name,
    and whether it's a weekend or today (if you pass `today_override`).

    Args:
        year: Four‑digit year (e.g., 2026).
        month: Month number (1‑12).
        first_weekday: "Monday" (default, ISO) or "Sunday".
        today_override: Optional ISO date (YYYY-MM-DD) to highlight
            as "today" in the grid. Usually you'd pass the `date` field
            returned by `get_current_datetime`.

    Returns:
        A structured dictionary with:
            - year, month, month_name
            - first_weekday
            - weeks: list of rows, each row a list of day objects
            - is_leap_year, days_in_month
    """
    result = _get_reference_calendar(year, month, first_weekday, today_override)
    return result.model_dump()




# =====================================================================
# Server
# =====================================================================

if __name__ == "__main__":
    print("🚀 Travel MCP Server running on http://127.0.0.1:8000/sse")
    mcp.run(transport="sse")           #llamaindex
    # mcp.run(transport="streamable-http") #langchain



# Flights to Greece
# What's the weather in Paris from 2026-07-16 to 2026-07-20?
# im on a budget of 1500 usd and i would need 30000 baht for thailand and then need remainig for my flight to mumbai do you think its enough?