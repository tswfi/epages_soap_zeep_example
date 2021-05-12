import os
from dotenv import load_dotenv

from epages_zeep import PriceListService
from zeep import xsd

load_dotenv()

pricelist_service = PriceListService(
    endpoint=os.getenv("ENDPOINT"),
    shopalias=os.getenv("SHOPALIAS"),
    username=os.getenv("USERALIAS"),
    password=os.getenv("PASSWORD"),
)

factory = pricelist_service.zeep.type_factory("ns0")

pricelistalias = os.getenv("PRICELISTALIAS")

res = pricelist_service.service.getInfo(
    PriceLists=factory.type_GetInfo_In([f"PriceLists/{pricelistalias}"]),
    Attributes=xsd.SkipValue,
    LanguageCodes=xsd.SkipValue,
)

print(res)
