from .base import BaseService


class ProductService(BaseService):
    """
    Product service wrapper

    Initializes ProductServiceXX.wsdl file
    """

    def __init__(self, endpoint="", shopalias="", username="", password="", wsdl=""):

        # build url to the wsdl file, note the version number here.
        self.wsdl = self._buildWSDLUrlFromEndPointAndService(
            endpoint=endpoint,
            service="ProductService",
            version="14",
        )

        # initialize the client
        super().__init__(
            endpoint=endpoint,
            shopalias=shopalias,
            username=username,
            password=password,
            wsdl=self.wsdl,
        )
