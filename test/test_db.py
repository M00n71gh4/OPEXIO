from db import (
list_groups,
list_incidents,
show_resolution,
list_machines,
list_errors,
list_resolved_statuses,

)   
def test_type_list_groups_none():
    assert type(list_groups()) == list
    
def test_type_list_groups_string():
    assert type(list_groups(machine_search="AG")) == list
    
def test_type_list_groups_number():
    assert type(list_groups(machine_search=2)) == list
    

    
# resolved=None, machine_id=None, start_date=None, end_date=None, note_search=None  
def test_type_list_incidents_none():
    assert type(list_incidents()) == list
    
def test_type_list_incidents_string():
    assert type(list_incidents(resolved="text", machine_id="text", start_date="text", end_date="text", note_search="text" )) == list
    
def test_type_list_incidents_number():
    assert type(list_incidents(resolved=1, machine_id=1, start_date=1, end_date=1, note_search=1)) == list
    
#machne_id=None, error_id=None, note_search=None
def test_type_show_resolution_none():
    assert type(show_resolution()) == list
    
def test_type_show_resolution_string():
    assert type(show_resolution(machne_id="text", error_id="text", note_search="text")) == list
    
def test_type_show_resolution_number():
    assert type(show_resolution(machne_id=1, error_id=1, note_search=1)) == list
    
    # group_id=None, machine_name=None
def test_type_list_machinesn_none():
    assert type(list_machines()) == list

def test_type_list_machines_string():
    assert type(list_machines(group_id="text", machine_name="text")) == list

def test_type_list_machines_number():
    assert type(list_machines(group_id=1, machine_name=1)) == list
    
# machine_id=None, error_number=None, error_name=None, description=None
def test_type_list_errors_none():
    assert type(list_errors()) == list

def test_type_list_errors_string():
    assert type(list_errors(machine_id="Text", error_number="Text", error_name="Text", description="Text")) == list
    
def test_type_list_errors_number():
    assert type(list_errors(machine_id=1, error_number=1, error_name=1, description=1)) == list

# None
def test_type_list_resolved_statuses_none():
    assert type(list_resolved_statuses()) == list
"""
def test_type_list_errors_string():
    assert type(list_resolved_statuses()) == list
    
def test_type_list_errors_number():
    assert type(list_resolved_statuses()) == list
"""