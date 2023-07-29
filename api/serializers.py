from rest_framework import serializers

from api import models


class InstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Instrument
        fields = "__all__"


class CoingeckoInstrumentOHLCSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CoingeckoInstrumentOHLC
        fields = "__all__"


class SyncHistorySerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(required=False)
    records_synced = serializers.IntegerField(read_only=True)
    sync_type = serializers.ChoiceField(models.SyncHistory.SYNC_CHOICES)
    extra_data = serializers.JSONField(read_only=True)

    class Meta:
        model = models.SyncHistory
        fields = "__all__"
