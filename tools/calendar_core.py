#tools/calendar_core.py

"""
calendar_core.py

Minimal general-calendar reference for an LLM travel agent.

Scope, deliberately narrow:
  1. Ground the agent in the real current date/time (LLMs don't reliably
     know "today", especially across timezones).
  2. Hand back a reference calendar grid (built on Python's stdlib
     `calendar` module) for a given month/year, so the agent can look up
     weekdays, month layout, and navigate relative dates ("next Friday",
     "last weekend of August") itself.

Date arithmetic, range-overlap checking, and conflict detection are
intentionally NOT here — the LLM does that reasoning itself using the
current date + the reference grid as ground truth.
"""

from __future__ import annotations

import calendar
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict


class CalendarError(ValueError):
    """Raised for invalid year/month/timezone input."""


# --------------------------------------------------------------------------
# Output models
# --------------------------------------------------------------------------

class CurrentDateTime(BaseModel):
    model_config = ConfigDict(extra="forbid")

    timezone: str
    iso_datetime: str
    date: str
    time_24h: str
    weekday_name: str
    day: int
    month: int
    month_name: str
    year: int


class CalendarDay(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: str  # ISO date, empty string if this cell is padding outside the month
    day: int  # 0 if padding
    weekday_name: str
    is_weekend: bool
    is_today: bool


class ReferenceCalendar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    year: int
    month: int
    month_name: str
    first_weekday: str  # which weekday each week row starts on
    weeks: list[list[CalendarDay]]
    is_leap_year: bool
    days_in_month: int


# --------------------------------------------------------------------------
# Core functions
# --------------------------------------------------------------------------

def get_current_datetime(tz_name: str = "UTC") -> CurrentDateTime:
    """
    Ground the agent in the real current date/time in a given timezone.
    Always call this before reasoning about relative dates ("tomorrow",
    "next Friday", "in three weeks") — never assume or guess today's date.
    """
    try:
        tz = ZoneInfo(tz_name)
    except Exception as e:
        raise CalendarError(
            f"Unknown timezone '{tz_name}'. Use an IANA name, e.g. 'Asia/Kolkata', "
            f"'America/New_York', 'UTC'."
        ) from e

    now = datetime.now(tz)
    return CurrentDateTime(
        timezone=tz_name,
        iso_datetime=now.isoformat(),
        date=now.date().isoformat(),
        time_24h=now.strftime("%H:%M:%S"),
        weekday_name=now.strftime("%A"),
        day=now.day,
        month=now.month,
        month_name=now.strftime("%B"),
        year=now.year,
    )


def get_reference_calendar(
    year: int,
    month: int,
    first_weekday: str = "Monday",
    today_override: Optional[str] = None,
) -> ReferenceCalendar:
    """
    Return a full reference calendar grid for a given month/year, so the
    agent can see weekday layout, count weekends, and navigate relative
    dates ("the second Saturday of August", "last weekday of the month")
    without guessing.

    Args:
        year: Four-digit year, e.g. 2026.
        month: Month number, 1-12.
        first_weekday: Which day each week row should start on — "Monday"
            or "Sunday" (default "Monday", ISO convention).
        today_override: Optional ISO date string (YYYY-MM-DD) to mark as
            "today" in the grid, e.g. the value returned by
            get_current_datetime. If omitted, no day is marked as today.
    """
    if not (1 <= month <= 12):
        raise CalendarError(f"month must be 1-12, got {month}.")
    if not (1 <= year <= 9999):
        raise CalendarError(f"year must be a plausible 4-digit year, got {year}.")

    weekday_map = {"monday": 0, "sunday": 6}
    key = first_weekday.strip().lower()
    if key not in weekday_map:
        raise CalendarError(
            f"first_weekday must be 'Monday' or 'Sunday', got '{first_weekday}'."
        )

    cal = calendar.Calendar(firstweekday=weekday_map[key])

    today_iso: Optional[str] = None
    if today_override:
        try:
            datetime.strptime(today_override, "%Y-%m-%d")
            today_iso = today_override
        except ValueError as e:
            raise CalendarError(
                f"today_override must be an ISO date YYYY-MM-DD, got '{today_override}'."
            ) from e

    weeks: list[list[CalendarDay]] = []
    for week in cal.monthdayscalendar(year, month):
        week_out = []
        for day in week:
            if day == 0:
                week_out.append(
                    CalendarDay(date="", day=0, weekday_name="", is_weekend=False, is_today=False)
                )
                continue
            d_date = f"{year:04d}-{month:02d}-{day:02d}"
            weekday_index = calendar.weekday(year, month, day)  # 0=Monday..6=Sunday
            week_out.append(
                CalendarDay(
                    date=d_date,
                    day=day,
                    weekday_name=calendar.day_name[weekday_index],
                    is_weekend=weekday_index >= 5,
                    is_today=(d_date == today_iso),
                )
            )
        weeks.append(week_out)

    return ReferenceCalendar(
        year=year,
        month=month,
        month_name=calendar.month_name[month],
        first_weekday=first_weekday.strip().capitalize(),
        weeks=weeks,
        is_leap_year=calendar.isleap(year),
        days_in_month=calendar.monthrange(year, month)[1],
    )