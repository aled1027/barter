from typing import Type

import adminactions.actions as actions
from django.contrib import admin
from django.contrib.admin import site
from django.db.models import Model

from api import models
from api.services import trade_evaluator


@admin.action(description="Retrieve OHLC for instrument")
def retrieve_ohlc(modeladmin, request, queryset):
    for instrument in queryset:
        trade_evaluator.sync_coingecko_ohlc(instrument)


def register_admin_for_models(
    model: Type[Model],
    in_list_display: list[str] | None = None,
    in_list_filter: list[str] | None = None,
    in_actions: list[str] | None = None,
):
    """
    This function registers an admin model given the configuration.

    Args:
        model (models): The model
        in_list_display (list[str] | None): The list of fields to display in the admin UI. If None, then all
            fields provided by model._meta.fields are displayed.
        in_list_filter (list[str] | None): List of filters
        in_actions (list[str] | None): List of actions
    """

    # Convert everything to tuples to avoid mutation
    default_list_display = ("__str__",) + tuple(
        field.name for field in model._meta.fields
    )
    the_list_display = tuple(in_list_display or default_list_display)
    the_list_filter = tuple(in_list_filter or [])
    the_actions = tuple(in_actions or [])

    class DynamicAdmin(admin.ModelAdmin):
        list_display = the_list_display
        list_filter = the_list_filter
        actions = the_actions

    admin.site.register(model, DynamicAdmin)


register_admin_for_models(models.Instrument, in_actions=[retrieve_ohlc])
register_admin_for_models(
    models.CoingeckoInstrumentOHLC, in_list_filter=["instrument", "date"]
)

register_admin_for_models(
    models.DydxCandle, in_list_filter=["instrument", "period_start", "period_end"]
)

register_admin_for_models(
    models.InvestmentCheck, in_list_filter=["instrument", "date", "dry_run"]
)

register_admin_for_models(
    models.Position,
    in_list_filter=["instrument", "base_instrument", "date_opened", "position_size"],
)


register_admin_for_models(
    models.SyncHistory, in_list_filter=["date", "sync_type", "records_synced"]
)

register_admin_for_models(models.Settings)


actions.add_to_site(site)
