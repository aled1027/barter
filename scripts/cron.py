import os

import django

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
django.setup()

from api.services.sync import do_trades, sync_dydx_candles

if __name__ == "__main__":
    sync_dydx_candles()
    do_trades()
