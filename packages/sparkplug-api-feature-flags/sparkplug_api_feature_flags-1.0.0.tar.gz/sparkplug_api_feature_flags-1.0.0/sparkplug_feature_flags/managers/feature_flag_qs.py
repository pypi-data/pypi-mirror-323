# django
from django.db.models import QuerySet

# typing
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import FeatureFlag  # noqa: F401


class FeatureFlagQS(
    QuerySet["FeatureFlag"],
):
    """Chainable queries should be defined here."""

