import logging
import logging.config
from jsonformatter import JsonFormatter
from collections import OrderedDict

from urllib.parse import urlparse
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Settings, Plugin
from zeep.transports import Transport
from zeep.loader import load_external

logger = logging.getLogger(__name__)


# All of this is just to get prettier debug logs in json format
class ExtraJsonFromatter(JsonFormatter):
    """
    Just a quick way to get mix_extra working

    see: https://github.com/MyColorfulDays/jsonformatter/issues/5
    """
    def __init__(self, fmt):
        super().__init__()
        self.mix_extra = True


logging.config.dictConfig(
    {
        "version": 1,
        "formatters": {
            "jsonformatter": {
                # "class": "jsonformatter.JsonFormatter",
                "()": ExtraJsonFromatter,
                "format": OrderedDict(
                    [
                        ("Name", "name"),
                        # ("Levelno", "levelno"),
                        ("Levelname", "levelname"),
                        # ("Pathname", "pathname"),
                        # ("Filename", "filename"),
                        ("Module", "module"),
                        ("Lineno", "lineno"),
                        ("FuncName", "funcName"),
                        ("Created", "created"),
                        # ("Asctime", "asctime"),
                        # ("Msecs", "msecs"),
                        # ("RelativeCreated", "relativeCreated"),
                        # ("Thread", "thread"),
                        # ("ThreadName", "threadName"),
                        # ("Process", "process"),
                        ("Message", "message"),
                    ]
                ),
            },
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "jsonformatter",
            },
        },
        "loggers": {
            "zeep.transports": {
                "level": "DEBUG",
                "propagate": True,
                "handlers": ["console"],
            },
            "epages_zeep": {
                "level": "DEBUG",
                "propagate": True,
                "handlers": ["console"],
            },
        },
    }
)
# end log configuration


class BaseService(object):
    """
    Base for ePages services

    :param endpoint: server to use e.g. https://example.com/
    :param shopalias: shop alias
    :param username: user alias
    :param password: password
    :param wsdl: wsdl file to use
    """

    def __init__(self, endpoint="", shopalias="", username="", password="", wsdl=""):

        self.endpoint = endpoint
        self.shopalias = shopalias
        self.username = username
        self.password = password
        self.wsdl = wsdl

        self.userpath = self._buildUserPath()

        arrayfixer = ArrayFixer()
        booleanfixer = BooleanFixer()

        session = Session()
        session.auth = HTTPBasicAuth(self.userpath, self.password)
        settings = Settings(
            strict=False,  # zeep does not like all of the ePages wsdl files
        )

        self.zeep = Client(
            wsdl=self.wsdl,
            settings=settings,
            transport=Transport(session=session),
            plugins=[arrayfixer, booleanfixer],
        )

        # add soapenc, xsd and xsi for array types and other values
        self.zeep.set_ns_prefix("soapenc", "http://schemas.xmlsoap.org/soap/encoding/")
        self.zeep.set_ns_prefix("xsd", "http://www.w3.org/2001/XMLSchema")
        self.zeep.set_ns_prefix("xsi", "http://www.w3.org/2001/XMLSchema-instance")

        # Always load older epagestypes, some of the responses still use it but
        # it is not correctly introduced in all of the wsdl files
        self.zeep.wsdl.types.add_document_by_url(self._buildOldEpagesTypesXSDUrl())

        # dump the whole wsdl for debugging
        # self.zeep.wsdl.dump()

        # get the binding name, there is only one so this should be ok
        qname = next(iter(self.zeep.wsdl.bindings))
        # and get the real service with the correct endpoint
        self.service = self.zeep.create_service(qname, self.endpoint)
        # logger.debug('service generated: ' + qname)

    def _buildUserPath(self):
        """
        Build userpath for authentication
        """
        return f"/Shops/{self.shopalias}/Users/{self.username}"

    def _buildWSDLUrlFromEndPointAndService(self, endpoint="", service="", version=""):
        """
        Build url to wsdl file from endpoint and service and version information
        """
        o = urlparse(endpoint)
        return f"{o.scheme}://{o.netloc}/WebRoot/WSDL/{service}{version}.wsdl"

    def _buildOldEpagesTypesXSDUrl(self):
        """
        Build url to wsdl file from endpoint and service and version information
        """
        o = urlparse(self.endpoint)
        return f"{o.scheme}://{o.netloc}/WebRoot/WSDL/EpagesTypes.xsd"


class BooleanFixer(Plugin):
    """
    ePages does not like boolean values as being "false"

    change them to 0

    TODO: add new elements that need this fix to the elements list
    """

    elements = (
        ".//IsClosed",
        ".//IsClosedTemporarily",
        ".//IsTrialShop",
        ".//IsInternalTestShop",
        ".//MarkedForDelete",
        ".//IsInternalTestShop",
        ".//HasSSLCertificate",
    )

    def egress(self, envelope, http_headers, operation, binding_options):

        for elementkey in self.elements:
            element = envelope.find(elementkey)
            if element is not None and element.text == "false":
                element.text = "0"

        return envelope, http_headers


class ArrayFixer(Plugin):
    """
    Mangle soap arrays for Soap::Lite

    see https://github.com/mvantellingen/python-zeep/issues/521

    TODO: add new elements that need this fix to the elements list
    """

    elements = (
        ".//Products",
        ".//Attributes",
        ".//LanguageCodes",
        ".//PriceLists",
        ".//ScalePrices",
    )

    def egress(self, envelope, http_headers, operation, binding_options):
        """
        force array type to elements that need to be arrays
        """

        for elementkey in self.elements:
            envelope = self._mangleToArrayType(envelope, elementkey)

        return envelope, http_headers

    def _mangleToArrayType(self, envelope, element):
        """
        Do one element
        """
        elements = envelope.find(element)
        if elements is not None:
            # logger.debug(f"Mangling '{element}', to soap enc arraytype")
            length = len(elements)
            elements.attrib[
                "{http://schemas.xmlsoap.org/soap/encoding/}arrayType"
            ] = f"xsd:anyType[{length}]"

        return envelope
