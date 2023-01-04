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
import pytest
from satellite._utils import camel_to_snake_case


@pytest.mark.parametrize(
    ["input_str", "expected_str"],
    [("aThing", "a_thing"), ("anotherVariable", "another_variable")],
)
def test_camel_to_snake_case(input_str: str, expected_str: str) -> None:
    assert camel_to_snake_case(input_str) == expected_str
