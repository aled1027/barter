import datetime as dt
from decimal import Decimal
from typing import Any

import pandas as pd
import structlog
from django.utils import timezone

from api import models

logger = structlog.get_logger(__name__)


def fetch_close(instrument: models.Instrument, in_date: dt.date) -> Decimal:
    """Fetches the closing price of an instrument at a particular date"""

    try:
        date = timezone.make_aware(in_date)
    except ValueError:
        date = in_date

    qs = models.DydxCandle.objects.filter(instrument=instrument)
    greater = qs.filter(period_end__gte=date).order_by("period_end").first()
    less = qs.filter(period_end__lte=date).order_by("-period_end").first()

    if greater and less:
        closest_record = (
            greater
            if abs(greater.period_end - date) < abs(less.period_end - date)
            else less
        )
    else:
        closest_record = greater or less

    if closest_record is None:
        raise ValueError("Record not found")

    return closest_record.close


def fetch_candles(
    instrument: models.Instrument, start: dt.datetime, end: dt.datetime
) -> models.DydxCandle:
    """start is inclusive, end is exclusive"""
    # Assume one candle per day
    qs = models.DydxCandle.objects.filter(
        instrument=instrument, period_end__gte=start, period_end__lt=end
    ).order_by("period_end")
    return qs


def fetch_prices_as_dataframe(
    instruments: list[models.Instrument], start: dt.datetime, end: dt.datetime
) -> pd.DataFrame:
    df = pd.DataFrame()
    for instr in instruments:
        candles = fetch_candles(instr, start, end)
        closes = [candle.close for candle in candles]
        df[instr.symbol] = closes

    df = df.astype(float)
    return df


def compute_instrument_correlation(
    instr1: models.Instrument,
    instr2: models.Instrument,
    start: dt.datetime,
    end: dt.datetime,
) -> float:
    df = fetch_prices_as_dataframe([instr1, instr2], start, end)
    return df.corr().iloc[0, 1]


def evaluate_trade(
    instr: models.Instrument, base: models.Instrument, date: dt.datetime
) -> dict[Any]:
    # Collect a bunch of data as we're going for returning
    ret = {
        "instr": instr.symbol,
        "base": base.symbol,
        "date": date.isoformat(),
        "open_position": False,
        "error": False,
    }

    try:
        # 1. Check if we have a position, of we do, continue
        if models.Position.objects.filter(
            instrument=instr, base_instrument=base
        ).first():
            ret["reason"] = "Already have a position"
            return ret

        # 2. Check if instr is correlated with base over the last 30 days
        corr_30d = compute_instrument_correlation(
            instr, base, date - dt.timedelta(days=30), date
        )
        ret["corr_30d"] = corr_30d
        if corr_30d < 0.5:
            ret["reason"] = "30 day correlation is too low"
            return ret

        # 3. Check if instr is inversely correlated with base over the last 4 days
        corr_4d = compute_instrument_correlation(
            instr, base, date - dt.timedelta(days=4), date
        )
        ret["corr_4d"] = corr_4d
        if corr_4d > -0.25:
            ret["reason"] = "4 day correlation is too high"
            return ret

        # 4. Check if base is up over the last 4 days
        base_4d = fetch_close(base, date - dt.timedelta(days=4))
        base_now = fetch_close(base, date)
        base_diff_4d = float((base_now - base_4d) / base_4d)
        ret["base_diff_4d"] = base_diff_4d
        if base_diff_4d < 0:
            ret["reason"] = "Base is down over the last 4 days"
            return ret

        # All the criteria passed
        ret["open_position"] = True
        return ret
    except Exception as e:
        logger.error("Error evaluating trade of {}".format(instr), exc_info=e)
        ret["error"] = True
        ret["open_position"] = False
        return ret
