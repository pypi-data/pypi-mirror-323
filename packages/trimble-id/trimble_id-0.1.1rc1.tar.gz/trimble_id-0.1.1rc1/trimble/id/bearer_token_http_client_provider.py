from .http_client import HttpClient
from ._version import VERSION

class BearerTokenHttpClientProvider:
    """
    A HttpClient provider for APIs using Bearer token authorization
    """
    def __init__(self, token_provider, base_address, default_headers = {}, product_name=None):
        """
        Initialize Bearer token http client provider

        :param token_provider: A token provider that provides the access token for the authenticated application or user
        :param base_address: The base address for the API that will be called
        :param default_headers: If any default address to be applied in Http request call. (Optional)
        :param product_name: Specify product name of consuming application (optional)
        """
        self._tokenProvider = token_provider
        self._baseAddress = base_address
        self._defaultHeaders = default_headers
        self._version = VERSION
        self._consumerKey = self.retrieve_consumer_key()

    async def retrieve_client(self):
        """
        Retrieves a preconfigured HttpClient to access a given API

        :return: A preconfigured HttpClient to access any given API
        """
        token = await self._tokenProvider.retrieve_token()
        
        if 'trimblepaas.com' in self._baseAddress:
            url = self._baseAddress + 'api/'
        else:
            url = self._baseAddress

        url = self._add_trailing_slash(url)

        return HttpClient(url, { **self._defaultHeaders, **{ 'authorization': 'Bearer ' + token } })

    def _add_trailing_slash(self, url):
        if url.endswith('/'):
            return url
        return url + '/'
    
    def retrieve_consumer_key(self):
        if (self._tokenProvider != None) : 
            return self._tokenProvider._consumerKey
        return None
    
