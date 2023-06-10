# accounts.serializers
from rest_framework import serializers

from accounts.models import PersonalAccessToken, User, UserWallet


class UserWalletCreateRequest(serializers.Serializer):
    wallet = serializers.CharField(required=True)
    chain = serializers.IntegerField(required=True)
    timestamp = serializers.IntegerField(required=True)
    signature = serializers.CharField(required=True)


class UserWalletCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWallet
        fields = "__all__"


class UserWalletUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWallet
        fields = ["is_active"]


class UserSerializer(serializers.ModelSerializer):
    wallets = UserWalletCreateSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "displayname",
            "avatar",
            "clan",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "wallets",
        ]


class UserPublicSerializer(serializers.ModelSerializer):
    """This model should be used for showing user information to other users."""

    class Meta:
        model = User
        fields = ["id", "username", "displayname", "avatar", "clan"]


class UserUpdateSerializer(serializers.ModelSerializer):
    """This model should be used for updating user profiles."""

    class Meta:
        model = User
        fields = ["displayname", "clan"]


class PatSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalAccessToken
        fields = ["id", "name", "valid_until", "created_at", "user"]
