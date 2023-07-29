from django.db import models

# Create your models here.


class Instrument(models.Model):
    name = models.CharField(max_length=200, blank=True, null=False)
    symbol = models.CharField(max_length=40, unique=True, blank=True, null=False)
    coingecko_id = models.CharField(max_length=100, blank=True, null=False)
    dydx_market_id = models.CharField(max_length=100, blank=True, null=False)
    enable_dydx_trades = models.BooleanField(default=True, null=False)

    def __str__(self):
        return self.name


class CoingeckoInstrumentOHLC(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, null=False)
    date = models.DateTimeField(help_text="Date of the OHLC", null=False)
    open = models.DecimalField(
        max_digits=30, decimal_places=8, null=False, help_text="Opening price"
    )
    high = models.DecimalField(
        max_digits=30, decimal_places=8, null=False, help_text="High price"
    )
    low = models.DecimalField(
        max_digits=30, decimal_places=8, null=False, help_text="Low price"
    )
    close = models.DecimalField(
        max_digits=30,
        decimal_places=8,
        null=False,
        help_text="Closing price",
    )

    def __str__(self):
        return "OHLC of {} on {}".format(self.instrument, self.date)


class DydxCandle(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, null=False)
    period_start = models.DateTimeField(help_text="Date of the OHLC", null=False)
    period_end = models.DateTimeField(help_text="Date of the OHLC", null=False)
    resolution = models.CharField(max_length=10, blank=True, null=False)
    open = models.DecimalField(
        max_digits=30, decimal_places=8, null=False, help_text="Opening price"
    )
    high = models.DecimalField(
        max_digits=30, decimal_places=8, null=False, help_text="High price"
    )
    low = models.DecimalField(
        max_digits=30, decimal_places=8, null=False, help_text="Low price"
    )
    close = models.DecimalField(
        max_digits=30,
        decimal_places=8,
        null=False,
        help_text="Closing price",
    )

    def __str__(self):
        return "DyDx Candle of {} on {}".format(self.instrument, self.period_end)


class InvestmentCheck(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, null=False)
    date = models.DateTimeField(null=False)
    dry_run = models.BooleanField(default=True, null=False)
    would_invest = models.BooleanField(default=None, null=True)
    extra_data = models.JSONField(null=False, blank=True, default=dict)


class SyncHistory(models.Model):
    SYNC_CHOICES = (
        ("prices", "Prices"),
        ("trades", "Trades"),
        ("dydx_candles", "DyDx Candles"),
    )

    date = models.DateTimeField(null=False)
    records_synced = models.IntegerField(null=False, default=0)
    sync_type = models.CharField(max_length=20, choices=SYNC_CHOICES, default="prices")
    extra_data = models.JSONField(null=False, blank=True, default=dict)


class Position(models.Model):
    instrument = models.ForeignKey(
        Instrument, on_delete=models.CASCADE, null=False, related_name="positions"
    )
    base_instrument = models.ForeignKey(
        Instrument, on_delete=models.CASCADE, null=False, related_name="base_positions"
    )
    position_size = models.FloatField(null=False)

    input_instr_price = models.FloatField(null=False)
    input_base_price = models.FloatField(null=False)
    extra_data = models.JSONField(null=False, blank=True, default=dict)

    date_opened = models.DateTimeField(null=False, auto_now_add=True)

    date_created = models.DateTimeField(null=False, auto_now_add=True)
    date_modified = models.DateTimeField(null=False, auto_now=True)


class Settings(models.Model):
    enable_trades = models.BooleanField(default=False, null=False)
