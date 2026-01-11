

def test_insert_group(ids):
    assert isinstance(ids["group_id"], int)

def test_insert_machine(ids):
    assert isinstance(ids["machine_id"], int)

def test_insert_error(ids):
    assert isinstance(ids["error_id"], int)


