#  Copyright (c) University College London Hospitals NHS Foundation Trust
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
# limitations under the License.
import faker

from typing import Any, Optional
from datetime import datetime, date, timedelta
from faker.providers import BaseProvider
from faker.providers.date_time import Provider as FakerDTProvider
from satellite._settings import EnvVar


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

    def _value_or_none(self, value: Any, p: float = 0.5) -> Optional[Any]:
        """Return the value or None dependent on the probability"""
        return value if self.generator.random.random() > p else None

    def source_system(self) -> str:
        """System which this row was created from"""
        return self.random_element(["source_a", "source_b"])

    def nhs_number(self) -> Optional[str]:
        """NHS number is a 10 digit numeric value"""
        return self._value_or_none(self.bothify(10 * "#"), p=0.1)


class _StarDatetimeProvider(FakerDTProvider):
    def timestamptz(self) -> datetime:
        return self.date_time()

    def valid_from(self) -> datetime:
        """
        Valid from is when EMAP star last updated this row. This is likely after ~2018
        """
        return datetime(2018, 1, 1) + timedelta(seconds=self.unix_time())

    def stored_from(self) -> datetime:
        """Valid from is when EMAP star first stored this row"""
        return self.valid_from()

    def date(self, **kwargs: Any) -> date:
        return self.date_between(
            date.fromisoformat("1970-01-01"), date.fromisoformat("2022-01-01")
        )


class _Faker(faker.Faker):
    """Custom Faker"""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

        for provider in (_StarBaseProvider, _StarDatetimeProvider):
            self.add_provider(provider)

    @classmethod
    def with_seed(cls, seed: int) -> "_Faker":
        """Faker instance with a defined seed"""
        _fake = cls()
        cls.seed(seed)  # Note: cannot set on an instance
        return _fake


fake = _Faker.with_seed(EnvVar("FAKER_SEED").unwrap_as(int))
