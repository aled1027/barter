# accounts.serializers
from rest_framework import serializers

from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
        ]


class UserPublicSerializer(serializers.ModelSerializer):
    """This model should be used for showing user information to other users."""

    class Meta:
        model = User
        fields = ["id", "username"]
