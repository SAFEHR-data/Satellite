import faker

from typing import Any
from datetime import datetime, date
from faker.providers import BaseProvider
from faker.providers.date_time import Provider as FakerDTProvider


class _StarBaseProvider(BaseProvider):
    """
    Provider for fake data in an EMAP star schema.
    The provider methods must be named as snake_case version of the
    column names or as the postgres sql types that will be used, the
    latter used as a fallback
    """

    @staticmethod
    def default() -> str:
        return ""

    def mrn(self) -> str:
        return self.bothify("#########")

    def bigint(self) -> int:
        return self.random_int()

    def text(self) -> str:
        return self.bothify("?????")

    def boolean(self) -> bool:
        return bool(self.random_int(0, 1))

    def real(self) -> float:
        return float(self.random_int(0, 1000)) / 100.0

    def bytea(self) -> str:
        return self.text()  # Encoding happens in the format specifier


class _StarDatetimeProvider(FakerDTProvider):
    def timestamptz(self) -> datetime:
        return self.date_time()

    def date(self) -> date:
        return self.date_between(
            date.fromisoformat("1970-01-01"), date.fromisoformat("2022-01-01")
        )


class Faker(faker.Faker):
    """Custom Faker"""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

        for provider in (_StarBaseProvider, _StarDatetimeProvider):
            self.add_provider(provider)

    @classmethod
    def with_seed(cls, seed: int) -> "Faker":
        """Faker instance with a defined seed"""
        _fake = cls()
        cls.seed(seed)  # Note: cannot set on an instance
        return _fake
