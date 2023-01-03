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
