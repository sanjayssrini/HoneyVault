import re

def validate(vault):
    assert "@" in vault["email"]
    assert len(vault["password"]) >= 6
    assert isinstance(vault["notes"], str)
    return True
