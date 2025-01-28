import pytest
from onepage_tools._internal.api_logic import InternalClass

@pytest.fixture
def internal_class_instance():
    return InternalClass()

def test_validate_token_logic(internal_class_instance):
    """
    Tests the token validation logic in InternalClass.
    """
    result = internal_class_instance.validate_token("3d34293a-ce28-4608-b65e-f3942282788b")
    assert isinstance(result, str), "Result should be a string."

def test_search_logic(internal_class_instance):
    """
    Tests the search logic in InternalClass.
    """
    result = internal_class_instance.search_query("3d34293a-ce28-4608-b65e-f3942282788b", "pooran@get1page.com")
    assert isinstance(result, str), "Result should be a string."
