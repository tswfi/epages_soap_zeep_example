import os
from dotenv import load_dotenv

from epages_zeep import PriceListAssignmentService

load_dotenv()

pricelistassignment_service = PriceListAssignmentService(
    endpoint=os.getenv("ENDPOINT"),
    shopalias=os.getenv("SHOPALIAS"),
    username=os.getenv("USERALIAS"),
    password=os.getenv("PASSWORD"),
)
factory = pricelistassignment_service.zeep.type_factory("ns0")

# pricelistassignment_service.zeep.wsdl.dump()

productalias = os.getenv("PRODUCTALIAS")
pricelistalias = os.getenv("PRICELISTALIAS")

res = pricelistassignment_service.service.getQuantityDiscounts(
    Products=factory.type_GetQuantityDiscounts_In([f"Products/{productalias}"]),
    PriceLists=factory.type_PriceLists_In([f"PriceLists/{pricelistalias}"]),
)

print(res)
