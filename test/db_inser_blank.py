import pytest
from db import (
setup_database, 
insert_group,
insert_machine,
insert_resolved,
insert_incident,
insert_resolution,
insert_error
)

# With no input, these functions should return None
def test_insert_blank_group():
    assert insert_group() == None

def test_insert_blank_machine():
    assert insert_machine() == None
    
def test_insert_blank_resolved():
    assert insert_resolved() == None
    
def test_insert_blank_incident():
    assert insert_incident() == None
    
def test_insert_blank_resolution():
    assert insert_resolution() == None
    
def test_insert_blank_error():
    assert insert_error() == None