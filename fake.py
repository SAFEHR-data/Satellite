import faker
from faker.providers import BaseProvider


class Faker(faker.Faker):
    """Custom Faker"""

    @classmethod
    def with_providers(cls, *providers):
        """Create a Faker instance with a set of providers"""

        self = cls()
        for provider in providers:
            self.add_provider(provider)

        return self


class MRNProvider(BaseProvider):

    def mrn(self) -> str:
        return self.bothify("#########")


fake = Faker.with_providers(
    MRNProvider
)
Faker.seed(0)
