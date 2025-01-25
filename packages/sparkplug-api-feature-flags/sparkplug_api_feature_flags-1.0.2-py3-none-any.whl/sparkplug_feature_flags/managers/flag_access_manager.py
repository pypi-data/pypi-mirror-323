# python
from typing import TYPE_CHECKING

# django
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models

# app
from .flag_access_qs import FlagAccessQS

if TYPE_CHECKING:
    from ..models import FlagAccess  # noqa: F401


class FlagAccessManager(
    models.Manager["FlagAccess"],
):
    # Define a default queryset for the manager.
    # This is used by self.all()
    def get_queryset(self) -> FlagAccessQS:
        return FlagAccessQS(self.model, using=self._db)

    def feature_flag_ids(self, *, user: type[AbstractBaseUser]) -> FlagAccessQS:
        return (
            self.all()
            .filter(user=user)
            .values_list(
                "feature_flag__id",
                flat=True,
            )
        )

    def get_for_user(self, *, user: type[AbstractBaseUser]) -> FlagAccessQS:
        return (
            self.all()
            .filter(user=user)
            .select_related("user")
            .select_related("feature_flag")
        )
