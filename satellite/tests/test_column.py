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
from satellite._column import Column


def test_boolean_column():

    column = Column(
        name="alive", java_type="Boolean", parent_table_name="core_demographic"
    )

    assert "column" in repr(column).lower()
    assert column.sql_type == "boolean"
    assert not column.is_foreign_key
    assert not column.is_primary_key
    assert column.faker_method() in (True, False)
