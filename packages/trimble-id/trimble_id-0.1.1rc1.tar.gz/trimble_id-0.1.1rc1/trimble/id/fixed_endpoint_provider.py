from ._version import VERSION

class FixedEndpointProvider:
    """
    An endpoint provider that returns fixed OAuth endpoints
    """
    def __init__(
            self, 
            authorization_endpoint, 
            token_endpoint, 
            userinfo_endpoint, 
            token_revocation_endpoint = None, 
            jwks_endpoint = None, 
            product_name = None):
        """
        Initialize FixedEndpointProvider class

        :param authorization_endpoint: Set Authorization Endpoint
        :param token_endpoint: Set Token Endpoint
        :param userinfo_endpoint: Set UserInfo Endpoint
        :param token_revocation_endpoint: Set Token revocation Endpoint
        :param jwks_endpoint: Set JSON Web key set Endpoint
        :param product_name: Product name of the consuming application (optional)
        """
        self._authorizationEndpoint = authorization_endpoint
        self._tokenEndpoint = token_endpoint
        self._userInfoEndpoint = userinfo_endpoint
        self._tokenRevocationEndpoint = token_revocation_endpoint
        self._jwksEndpoint = jwks_endpoint
        self._version = VERSION

    async def retrieve_authorization_endpoint(self):
        """
        Retrieves a fixed Authorization endpoint
        """
        return self._authorizationEndpoint

    async def retrieve_token_endpoint(self):
        """
        Retrieves a fixed Token endpoint
        """
        return self._tokenEndpoint

    async def retrieve_json_web_keyset_endpoint(self):
        """
        Retrieves a fixed JSON Web key set endpoint
        """
        return self._jwksEndpoint