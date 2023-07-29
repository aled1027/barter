import datetime as dt

import pytest
from django.core.management import call_command
from django.test import Client

from accounts.models import User
from api.models import DydxCandle, Instrument
from api.services.trade_evaluator import (
    compute_instrument_correlation,
    evaluate_trade,
    fetch_prices_as_dataframe,
)

# Create your tests here.


@pytest.fixture
def load_data(db):
    call_command("loaddata", "fixtures/instruments.json")
    call_command("loaddata", "fixtures/dydx_candles.json")
    User.objects.create_superuser("admin", "admin@test.com", "adminpassword")


@pytest.fixture
def client(load_data):
    client = Client()
    client.login(username="admin", password="adminpassword")
    return client


def test_fixtures(load_data):
    """Tests that the fixtures were loaded correctly"""
    assert Instrument.objects.count() == 6
    assert DydxCandle.objects.count() == 198


def test_fetch_prices_as_dataframe(load_data):
    instruments = Instrument.objects.filter(symbol__in=["ETH", "DOGE"])
    start = dt.datetime(2023, 6, 10)
    end = dt.datetime(2023, 6, 12)
    prices_df = fetch_prices_as_dataframe(instruments, start, end)

    expected_dict = {
        "ETH": {0: 1752.3, 1: 1753.3},
        "DOGE": {0: 0.0617, 1: 0.0616},
    }
    assert prices_df.to_dict() == expected_dict


def test_instrument_correlation(load_data):
    doge = Instrument.objects.get(symbol="DOGE")
    eth = Instrument.objects.get(symbol="ETH")
    start = dt.datetime(2023, 6, 10)
    end = dt.datetime(2023, 6, 12)
    corr = compute_instrument_correlation(doge, eth, start, end)
    assert corr == pytest.approx(-1)


def test_evaluate_trade(load_data):
    kap = Instrument.objects.get(symbol="DOGE")
    eth = Instrument.objects.get(symbol="ETH")
    start = dt.datetime(2023, 6, 12)
    res = evaluate_trade(kap, eth, start)

    expected = {
        "base": "ETH",
        "corr_30d": 0.49580718990328376,
        "date": "2023-06-12T00:00:00",
        "instr": "DOGE",
        "open_position": False,
        "reason": "30 day correlation is too low",
    }
    assert res == expected
