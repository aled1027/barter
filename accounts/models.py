from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    something = models.CharField(max_length=150)  # type: ignore
