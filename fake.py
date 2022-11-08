import faker
from faker.providers import BaseProvider
from faker.providers.date_time import Provider as FakerDTProvider
from datetime import datetime, date


class Faker(faker.Faker):
    """Custom Faker"""

    @classmethod
    def with_providers(cls, *providers):
        """Create a Faker instance with a set of providers"""

        self = cls()
        for provider in providers:
            self.add_provider(provider)

        return self


class EMAPBaseProvider(BaseProvider):
    """
    Provider for fake data in an EMAP star schema.
    The provider methods must be named as snake_case version of the
    column names or as the postgres sql types that will be used, the
    latter used as a fallback
    """

    @staticmethod
    def default() -> str:
        return fake.bothify("??????")

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

    def bytes(self) -> bytes:
        return self.default().encode()


class EMAPDatetimeProvider(FakerDTProvider):

    def timestamptz(self) -> datetime:
        return self.date_time()

    def date(self) -> date:
        return self.date_between(
            date.fromisoformat("1970-01-01"),
            date.fromisoformat("2022-01-01")
        )


fake = Faker.with_providers(
    EMAPBaseProvider,
    EMAPDatetimeProvider
)
Faker.seed(0)
