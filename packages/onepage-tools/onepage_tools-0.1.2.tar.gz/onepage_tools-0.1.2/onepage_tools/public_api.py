from ._internal.api_logic import InternalClass
from typing import Dict

class PublicAPI:
    def __init__(self):
        self._internal = InternalClass()

    def validate_token(self, token: str) -> str:
        """
        Public method to validate a token.

        :param token: The API token to validate.
        :return: Validation message.
        """
        return self._internal.validate_token(token)

    def search(self, token: str, query: str) -> str:
        """
        Public method to perform a search.

        :param token: API token for authentication.
        :param query: Search query.
        :return: Search results or error message.
        """
        return self._internal.search_query(token, query)



