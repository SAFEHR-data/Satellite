import pytest
from satellite._utils import camel_to_snake_case


@pytest.mark.parametrize(
    ["input_str", "expected_str"],
    [("aThing", "a_thing"), ("anotherVariable", "another_variable")],
)
def test_camel_to_snake_case(input_str: str, expected_str: str) -> None:
    assert camel_to_snake_case(input_str) == expected_str
