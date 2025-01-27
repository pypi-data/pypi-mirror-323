from ._version import VERSION

class FixedKeySetProvider:
    """
    A keyset provider that returns a fixed keyset
    """
    def __init__(self, keyset, product_name = None):      
        """
        Initialize FixedKeySetProvider class

        :param keyset: A dictionary of named keys
        :param product_name: Product name of consuming application
        """  
        self._keyset = keyset

        self._version = VERSION

    async def retrieve_keyset(self):
        """
        Retrieves a dictionary of named keys

        :return: Fixed Keyset
        """
        return self._keyset