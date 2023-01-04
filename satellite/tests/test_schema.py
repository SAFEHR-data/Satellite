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

from satellite.main import star


def test_basic_properties_of_non_connected_schema():

    assert star.schema_name == "star"
    assert not star.exists
    assert "create schema" in star.schema_create_command.lower()

    with pytest.raises(AssertionError):  # must be connected to update num rows
        star.update_num_rows_in_tables()
