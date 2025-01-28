import pytest
from onepage_tools.public_api import PublicAPI

@pytest.fixture
def public_api_instance():
    return PublicAPI()

def test_validate_token(public_api_instance):
    """
    Tests the validate_token method in PublicAPI.
    """
    result = public_api_instance.validate_token("3d34293a-ce28-4608-b65e-f3942282788b")
    assert isinstance(result, str), "Result should be a string."

def test_search(public_api_instance):
    """
    Tests the search method in PublicAPI.
    """
    result = public_api_instance.search("3d34293a-ce28-4608-b65e-f3942282788b", "pooran@get1page.com")
    assert isinstance(result, str), "Result should be a string."
