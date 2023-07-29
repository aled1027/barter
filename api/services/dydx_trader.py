import os
import time

import structlog
from dydx3 import Client

from api.services.dydx_models import CandlesModel

logger = structlog.get_logger()

# https://github.com/dydxprotocol/dydx-v3-python/blob/master/dydx3/constants.py
from dydx3.constants import (
    API_HOST_MAINNET,
    NETWORK_ID_MAINNET,
    ORDER_SIDE_BUY,
    ORDER_SIDE_SELL,
    ORDER_TYPE_LIMIT,
)
from web3 import Web3


class DydxTrader:
    def __init__(self) -> None:
        eth_private_key = os.environ["ETH_PRIVATE_KEY"]
        eth_public_key = os.environ["ETH_PUBLIC_KEY"]
        web3_provider_url = os.environ["WEB3_PROVIDER_URL"]

        self.client = Client(
            network_id=NETWORK_ID_MAINNET,
            host=API_HOST_MAINNET,
            default_ethereum_address=eth_public_key,
            eth_private_key=eth_private_key,
            web3=Web3(Web3.HTTPProvider(web3_provider_url)),
        )

        stark_key_pair_with_y_coordinate = self.client.onboarding.derive_stark_key()
        self.client.stark_private_key = stark_key_pair_with_y_coordinate["private_key"]
        self.markets = self.client.public.get_markets().data

    def get_position_id(self) -> str:
        account_response = self.client.private.get_account()
        position_id = account_response.data["account"]["positionId"]
        return position_id

    def get_price(self, market: str) -> float:
        # https://dydxprotocol.github.io/v3-teacher/#get-markets
        price = float(self.markets["markets"][market]["indexPrice"])
        return self._format_price(price, market)

    def _format_price(self, price: float, market: str) -> float:
        tick_size = float(self.markets["markets"][market]["tickSize"])

        # Round to the nearest tick size if needed
        if "." in str(tick_size):
            num_decimals = len(str(tick_size).split(".")[1])
            price = round(price, num_decimals)

        return price

    def _format_size(self, size: float, market: str) -> float:
        # Round to the nearest step size if needed

        step_size = float(self.markets["markets"][market]["stepSize"])
        if step_size < 1:
            num_decimals = len(str(step_size).split(".")[1])
            size = round(size, num_decimals)
        else:
            step_size = int(step_size)
            size = round(size, -1 * (len(str(step_size)) - 1))

        return size

    def block_until_no_pending_orders(self, timeout_seconds=120):
        sleep_time = 10  # seconds
        time_waited = 0
        while time_waited < timeout_seconds:
            orders = self.client.private.get_orders().data["orders"]
            # If there's no pending orders, we're done
            if not orders:
                return

            # otherwise, sleep and try again
            logger.debug("Sleeping {} seconds".format(sleep_time))
            time.sleep(sleep_time)
            time_waited += sleep_time

        raise TimeoutError("Timed out waiting for orders stop pending")

    def get_candles(self, market: str) -> CandlesModel:
        """
        https://dydxprotocol.github.io/v3-teacher/?python#get-candles-for-market
        """
        resp = self.client.public.get_candles(
            market=market,
            resolution="1DAY",
        )
        return CandlesModel(**resp.data)

    def short(self, market: str, price: float, size: float) -> dict:
        # https://dydxprotocol.github.io/v3-teacher/#create-a-new-order
        # https://github.com/chiwalfrm/dydxexamples

        position_id = self.get_position_id()
        price = self._format_price(price, market)
        size = self._format_size(size, market)

        logger.debug("Shorting {} {} at price {}".format(size, market, price))

        order_params = {
            "position_id": position_id,
            "market": market,
            "side": ORDER_SIDE_SELL,
            "order_type": ORDER_TYPE_LIMIT,
            "post_only": False,
            "size": str(
                size
            ),  # Size of the order, in base currency (i.e. an ETH-USD position of size 1 represents 1 ETH).
            "price": str(price),  # Worst accepted price of the base asset in USD.
            "limit_fee": "0.0015",
            "expiration_epoch_seconds": time.time() + 75,  # 75 seconds from now
        }
        order_response = self.client.private.create_order(**order_params)
        return {"order_params": order_params, "order_data": order_response.data}

    def long(self, market: str, price: float, size: float) -> dict:
        # https://dydxprotocol.github.io/v3-teacher/#create-a-new-order
        # https://github.com/chiwalfrm/dydxexamples

        position_id = self.get_position_id()
        price = self._format_price(price, market)
        size = self._format_size(size, market)

        logger.debug("Longing {} {} at price {}".format(size, market, price))

        order_params = {
            "position_id": position_id,
            "market": market,
            "side": ORDER_SIDE_BUY,
            "order_type": ORDER_TYPE_LIMIT,
            "post_only": False,
            "size": str(
                size
            ),  # Size of the order, in base currency (i.e. an ETH-USD position of size 1 represents 1 ETH).
            "price": str(price),  # Worst accepted price of the base asset in USD.
            "limit_fee": "0.0015",
            "expiration_epoch_seconds": time.time() + 75,  # 75 seconds from now
        }
        order_response = self.client.private.create_order(**order_params)
        order_response.data["order"]["id"]
        return {"order_params": order_params, "order_data": order_response.data}
