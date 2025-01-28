import requests
from typing import Optional

BASE_URL = "https://api.example.com"

class InternalClass:
    def __init__(self):
        self._api_key = "secret"  # Example private attribute

    def validate_token(self, token: str) -> str:
        """
        Validates the given API token.
        
        :param token: The API token to validate.
        :return: Validation status message.
        """
        url = f"https://abc55113.1pageplus.com/api/v2/0EA1B4B0"
        payload = {"token": token}
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                response_type = data.get("type")
                if response_type == "credits_data":
                    credits = data.get("data", {}).get("Credits", "N/A")
                    return f"Token validated successfully. Credits available: {str(credits)}"
                elif response_type == "no_credits":
                    return "Token is valid but no credits are available. Please buy credits to proceed."
                elif response_type == "invalid":
                    return "Invalid token. Please try again or exit."
                else:
                    return "Unexpected response type."
            else:
                return f"Token validation failed: {str(data.get('message'))}"
        else:
            return f"Error validating token: {str(response.text)}"

    def search_query(self, token: str, query: str) -> str:
        """
        Executes a search query using the provided token.

        :param token: The API token to authenticate the search.
        :param query: The search query.
        :return: Search results or error message.
        """
        url = f"https://abc55113.1pageplus.com/api/v2/F6DBDEC5"
        payload = {"s": query, "l": "en", "o": "content"}
        headers = {
            "Content-Type": "application/json",
            "authToken": token,
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get("success"):
                    if data.get("type") == "no_credits":
                        return "You have used all credits. Please purchase more."
                    elif data.get("type") == "error":
                        return "Sorry, couldn't find the results. Try again with a different input."
                    else:
                        return f"Search results: {str(data.get('data', 'No data available'))}"
                else:
                    return f"Search failed: {str(data.get('message', 'No error message provided'))}"
            except ValueError:
                return f"Search results: {response.text}"
        else:
            return f"Error during search: {response.text}"

