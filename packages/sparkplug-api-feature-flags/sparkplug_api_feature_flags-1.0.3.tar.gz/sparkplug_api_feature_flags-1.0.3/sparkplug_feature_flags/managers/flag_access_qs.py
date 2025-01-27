# django
from django.db.models import QuerySet

# typing
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import FlagAccess  # noqa: F401


class FlagAccessQS(
    QuerySet["FlagAccess"],
):
    """Chainable queries should be defined here."""

