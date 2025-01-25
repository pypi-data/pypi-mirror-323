# python
from typing import TYPE_CHECKING

# django
from django.db import models

# app
from .feature_flag_qs import FeatureFlagQS

if TYPE_CHECKING:
    from ..models import FeatureFlag  # noqa: F401


class FeatureFlagManager(
    models.Manager["FeatureFlag"],
):
    # Define a default queryset for the manager.
    # This is used by self.all()
    def get_queryset(self) -> FeatureFlagQS:
        return FeatureFlagQS(self.model, using=self._db)

    def list(self) -> FeatureFlagQS:
        return (
            self.all()
            .order_by("-created")
        )

    def active(self) -> FeatureFlagQS:
        return (
            self.all()
            .filter(enabled=True)
            .order_by("-created")
        )
