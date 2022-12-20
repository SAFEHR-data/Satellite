import os

from typing import Any


_default_values = {
    "STAR_SCHEMA_NAME": "star",
    "FAKER_SEED": "0",
    "INFORMDB_BRANCH_NAME": "master",
    "POSTGRES_HOST": "localhost",
    "N_TABLE_ROWS": "0"
}


class EnvVar:
    def __init__(self, name: str):
        self._name = name
        self._value = os.environ.get(name, None)

    def unwrap(self) -> str:
        """Raise a runtime error if the value is undefined"""
        if self._value is None:
            raise RuntimeError(
                f"${self._name} was unset. Ensure it is set as an environment variable"
            )
        return self._value

    def unwrap_as(self, _type: Any) -> Any:
        """Raise a runtime error if the value is undefined and cast as a type"""
        return _type(self.unwrap())

    def or_else(self, default: Any) -> str:
        """Return the value if set otherwise use the default value"""
        return default if self._value is None else self._value

    def or_default(self) -> str:
        """Return the value if it is set otherwise a default"""

        if self._value is not None:
            return self._value

        elif self._name in _default_values:
            return _default_values[self._name]

        raise RuntimeError(f"Failed to find a default for {self._name}")

    def __str__(self):
        return str(self._value)
