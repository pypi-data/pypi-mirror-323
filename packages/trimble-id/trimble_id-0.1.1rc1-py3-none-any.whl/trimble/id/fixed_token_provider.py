from ._version import VERSION

class FixedTokenProvider:
    """
    A token provider that returns a fixed token
    """
    def __init__(self, token, product_name = None):
        """
        Initialize FixedTokenProvider class

        :param token: Sets access token to FixedTokenProvider
        :param productName: Product name of the consuming application
        """
        self._token = token
        self._consumerKey = None
        self._version = VERSION
    
    def with_token(self, token):
        """
        Sets consumer key to FixedTokenProvider

        :param consumer_key: Sets consumer key to FixedTokenProvider
        """
        self._token = token
        return self

    async def retrieve_token(self):
        """
        Retrieves fixed token
        """
        return self._token
    