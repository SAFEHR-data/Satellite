import pytest

from satellite.main import star


def test_basic_properties_of_non_connected_schema():

    assert star.schema_name == "star"
    assert not star.exists
    assert "create schema" in star.schema_create_command.lower()

    with pytest.raises(AssertionError):  # must be connected to update num rows
        star.update_num_rows_in_tables()
