# python
from typing import TypeVar

# django
from django.contrib.auth.base_user import AbstractBaseUser

# contrib
from rest_framework.serializers import (
    ModelSerializer,
    SlugRelatedField,
)

# app
from ..models import (
    FeatureFlag,
    FlagAccess,
)
from .feature_flag_teaser import FeatureFlagTeaser


User = TypeVar("User", bound=AbstractBaseUser)


class FlagAccessRead(
    ModelSerializer["FlagAccess"],
):
    feature_flag_uuid: "SlugRelatedField[FeatureFlag]" = SlugRelatedField(
        slug_field="uuid",
        source="feature_flag",
        read_only=True,
    )

    feature_flag = FeatureFlagTeaser(read_only=True)

    user_uuid: "SlugRelatedField[User]" = SlugRelatedField(
        slug_field="uuid",
        source="user",
        read_only=True,
    )

    class Meta:
        model = FlagAccess

        fields = (
            "uuid",
            "feature_flag_uuid",
            "feature_flag",
            "user_uuid",
        )

        read_only_fields = ("__all__",)
