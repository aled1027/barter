import datetime as dt

import requests
import structlog
from django.utils import timezone

from api import models
from api.services import trade_evaluator
from api.services.dydx_models import DydxMarketsModel
from api.services.dydx_trader import DydxTrader
from api.services.positions import open_position

logger = structlog.get_logger(__name__)


def do_trades() -> None:
    date = dt.datetime.now()

    settings = models.Settings.objects.get(id=1)
    if settings.enable_trades is False:
        logger.warning("Trades are disabled, not opening position")

    extra_data = {}
    base = models.Instrument.objects.get(symbol="ETH")
    for instrument in models.Instrument.objects.filter(enable_dydx_trades=True):
        try:
            eval_trade_result = trade_evaluator.evaluate_trade(instrument, base, date)
            extra_data[instrument.symbol] = eval_trade_result

            if settings.enable_trades and eval_trade_result["open_position"]:
                open_position(instrument, base)
        except Exception as e:
            logger.error("Error processing {}".format(instrument), exc_info=e)

    sync_history = models.SyncHistory.objects.create(
        date=timezone.now(),
        sync_type="trades",
        extra_data=extra_data,
    )
    sync_history.save()


def sync_dydx_candles():
    trader = DydxTrader()

    for instrument in models.Instrument.objects.filter():
        logger.info("Processing instrument {}".format(instrument))
        if not instrument.dydx_market_id:
            logger.info(
                "Instrument {} doesn't have a dydx_market_id, Skipping dydx candle load.".format(
                    instrument
                )
            )
            continue

        candles = trader.get_candles(instrument.dydx_market_id)

        for candle in candles.candles:
            candle_started_at_dt = timezone.make_aware(
                dt.datetime.strptime(candle.startedAt, "%Y-%m-%dT%H:%M:%S.%fZ"),
                timezone.utc,
            )

            candle_ended_at_dt = timezone.make_aware(
                dt.datetime.strptime(candle.updatedAt, "%Y-%m-%dT%H:%M:%S.%fZ"),
                timezone.utc,
            )

            one_day_ago = timezone.make_aware(
                dt.datetime.now() - dt.timedelta(days=1), timezone.utc
            )
            if candle_started_at_dt > one_day_ago:
                logger.info("Skipping candle because candle is too new")
                continue

            if models.DydxCandle.objects.filter(
                instrument=instrument,
                period_start=candle.startedAt,
            ).first():
                # candle already exists, continue
                logger.info("Skipping candle because candle already exists")
                continue

            candle_model = models.DydxCandle.objects.create(
                instrument=instrument,
                period_start=candle_started_at_dt,
                period_end=candle_ended_at_dt,
                resolution=candle.resolution,
                open=candle.open,
                high=candle.high,
                low=candle.low,
                close=candle.close,
            )
            candle_model.save()

    sync_history = models.SyncHistory.objects.create(
        date=timezone.now(),
        sync_type="dydx_candles",
        extra_data={},
    )
    sync_history.save()


def sync_dydx_instruments():
    trader = DydxTrader()
    markets = DydxMarketsModel(markets=trader.markets["markets"])

    for _, market_data in markets.markets.items():
        symbol = market_data.baseAsset
        if models.Instrument.objects.filter(symbol=symbol).first():
            logger.info("Skipping instrument {}".format(symbol))
            continue

        # Create a model
        instrument = models.Instrument.objects.create(
            symbol=symbol,
            name=symbol,
            coingecko_id="",
            dydx_market_id=market_data.market,
            enable_dydx_trades=False,
        )
        instrument.save()
        logger.info("Created instrument {}".format(instrument.symbol))


def sync_coingecko_ohlc(instrument: models.Instrument) -> int:
    """
    This may be deprecated soon.

    This sync data from coingecko into the Coingecko OHLC table.
    """
    url = f"https://api.coingecko.com/api/v3/coins/{instrument.coingecko_id}/ohlc/"

    query_params = {"vs_currency": "usd", "days": "30"}

    resp = requests.get(url, params=query_params)
    if not resp.ok:
        logger.error(f"Error querying coingecko: {resp.text}")
        raise RuntimeError("Error querying coingecko: {}".format(resp.status_code))

    data = resp.json()
    num_records_created = 0

    # Always skip the newest value because it might be fully defined yet (i.e., in the middle of the interval)
    for entry in data[:-1]:
        # entry[0] is the timestamp in milliseconds, so divide by 1000 to get seconds
        date = dt.datetime.fromtimestamp(entry[0] // 1000)
        date = timezone.make_aware(date)

        open = entry[1]
        high = entry[2]
        low = entry[3]
        close = entry[4]

        # Check if an instrument already exists
        if not models.CoingeckoInstrumentOHLC.objects.filter(
            instrument=instrument, date=date
        ).exists():
            num_records_created += 1
            instrument_ohlc = models.CoingeckoInstrumentOHLC.objects.create(
                instrument=instrument,
                date=date,
                open=open,
                high=high,
                low=low,
                close=close,
            )
            instrument_ohlc.save()

    return num_records_created
