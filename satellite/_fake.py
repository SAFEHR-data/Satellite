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
from faker.providers.person.en import Provider as PersonProvider
from faker.providers.address.en import Provider as AddressProvider
from faker.providers.date_time import Provider as FakerDTProvider
from satellite._settings import EnvVar

_ETHNICITIES = [
            "Black African",
            "Black Other",
            "Chinese",
            "Filipino",
            "Indian",
            "Irish Traveller",
            "Mixed ethnic group",
            "Roma",
            "White",
            "Any other ethnic group",
            "Unknown",
]


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

    def bytea(self) -> bytes:
        return self.text().encode()

    def _value_or_none(self, value: Any, p: float = 0.5) -> Optional[Any]:
        """Return the value or None dependent on the probability"""
        return value if self.generator.random.random() > p else None

    def source_system(self) -> str:
        """System which this row was created from"""
        return self.random_element(["source_a", "source_b"])

    def nhs_number(self) -> Optional[str]:
        """NHS number is a 10 digit numeric value"""
        return self._value_or_none(self.bothify(10 * "#"), p=0.1)

    def ethnicity(self) -> str:
        return self.random_element(_ETHNICITIES)

    def sex(self) -> str:
        return self.random_element(["UNKNOWN", "M", "F"])

    def location_string(self) -> str:
        return f"T{self.random_int(0, 99):02d}-B{self.random_int(0, 99):02d}"

    def arrival_method(self) -> Optional[str]:
        value = self.random_element(["Ambulance", "Walk in"])
        return self._value_or_none(value, p=0.5)

    def encounter(self) -> str:
        return self.bothify("#########")

    @staticmethod
    def comments() -> None:
        return None


class _StarPersonProvider(PersonProvider, _StarBaseProvider):

    def firstname(self) -> str:
        return self.first_name().replace("'", " ")

    def middlename(self) -> str:
        return self._value_or_none(self.firstname(), p=0.5)

    def lastname(self) -> str:
        return self.last_name().replace("'", r" ")

    def name(self) -> str:
        return self.text()

    @staticmethod
    def patient_class() -> None:
        return None


class _StarDatetimeProvider(FakerDTProvider, _StarBaseProvider):
    def timestamptz(self) -> datetime:
        return self.date_time()

    def _recent_datetime(self) -> datetime:
        delta_time = timedelta(
            seconds=self.unix_time(start_datetime=datetime(2018, 1, 1),
                                   end_datetime=datetime(2023, 1, 1))
        )
        return datetime(1970, 1, 1) + delta_time

    def valid_from(self) -> datetime:
        """
        Valid from is when EMAP star last updated this row. This is likely after ~2018
        """
        return self._recent_datetime()

    def stored_from(self) -> datetime:
        """Valid from is when EMAP star first stored this row"""
        return self._recent_datetime()

    def date(self, **kwargs: Any) -> date:
        return self.date_between(
            date.fromisoformat("1970-01-01"), date.fromisoformat("2022-01-01")
        )

    def discharge_datetime(self) -> datetime:
        return self._value_or_none(self._recent_datetime(), p=0.1)


class _StarAddressProvider(AddressProvider):

    def home_postcode(self) -> str:
        return self.postcode()


_providers = (
    _StarBaseProvider,
    _StarDatetimeProvider,
    _StarPersonProvider,
    _StarAddressProvider,
)


class _Faker(faker.Faker):
    """Custom Faker"""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

        for provider in _providers:
            self.add_provider(provider)

    @classmethod
    def with_seed(cls, seed: int) -> "_Faker":
        """Faker instance with a defined seed"""
        _fake = cls()
        cls.seed(seed)  # Note: cannot set on an instance
        return _fake


fake = _Faker.with_seed(EnvVar("FAKER_SEED").unwrap_as(int))
