import time

import structlog

from api import models
from api.services.dydx_trader import DydxTrader

logger = structlog.get_logger(__name__)


def open_position(instr: models.Instrument, base: models.Instrument) -> models.Position:
    # Short at 10x leverage, and long the same amount of base at 10x leverage

    # leverage is implicit, based on the position size
    # Position size be a multiple of 20 because each
    # individual order must be a multiple of 10 for dydx

    sleep_time_seconds = 15
    pos_size_usd = 200  # size in usd
    trade_size_usd = pos_size_usd / 2.0

    trader = DydxTrader()

    # Short the instrument
    instr_price = trader.get_price(instr.dydx_market_id)
    instr_trade_size = trade_size_usd / instr_price

    trader.block_until_no_pending_orders()
    short_res = trader.short(instr.dydx_market_id, instr_price, instr_trade_size)

    # TODO: my guess is we dont need the sleep, we need a "check for pending orders"
    # function that blocks until that's good, then it sends in the order with some kind of timeout
    # trader.block_until_no_pending_orders(timeout=120_seconds)  and then raises TimeoutError if the timeout is hit.

    # Long the base
    base_price = trader.get_price(base.dydx_market_id)
    base_trade_size = trade_size_usd / base_price
    trader.block_until_no_pending_orders()
    long_res = trader.long(base.dydx_market_id, base_price, base_trade_size)

    # sleep to let the order go through. this may be needed for the position id to increment
    logger.debug("Sleeping {} seconds".format(sleep_time_seconds))
    time.sleep(sleep_time_seconds)

    extra_data = {
        "short": short_res,
        "long": long_res,
    }

    pos = models.Position.objects.create(
        instrument=instr,
        base_instrument=base,
        position_size=pos_size_usd,
        input_instr_price=instr_price,
        input_base_price=base_price,
        extra_data=extra_data,
    )
    pos.save()
    return pos


def close_position() -> None:
    # 6. When at X% profit or loss, close trade
    pass
