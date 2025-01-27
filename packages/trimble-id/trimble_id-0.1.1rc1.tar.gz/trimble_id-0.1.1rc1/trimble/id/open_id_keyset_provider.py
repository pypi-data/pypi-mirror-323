import json
import jwt

from .http_client import HttpClient
from ._version import VERSION

class OpenIdKeySetProvider:
    """
    A keyset provider based on the OAuth well known configuration
    """
    def __init__(self, endpoint_provider, product_name = None):
        """
        Initialize OpenIdKeySetProvider class

        :param endpoint_provider: An endpoint provider that provides the URL for the Trimble Identity JSON web keyset endpoint
        :param product_name: Product name of the consuming application
        """
        self._endpointProvider = endpoint_provider

        self._version = VERSION

    async def retrieve_keys(self):
        """
        Retrieves an dictionary of named keys
        """
        client = HttpClient('', {})
        result = await client.get_json(await self._endpointProvider.retrieve_jwks_endpoint(), {})
        self._keys = {}
        for jwk in result['keys']:
            kid = jwk['kid']
            self._keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
        return self._keys