import os
from dotenv import load_dotenv

from epages_zeep import ProductService

load_dotenv()

product_service = ProductService(
    endpoint=os.getenv("ENDPOINT"),
    shopalias=os.getenv("SHOPALIAS"),
    username=os.getenv("USERALIAS"),
    password=os.getenv("PASSWORD"),
)

factory = product_service.zeep.type_factory("ns0")

productalias = os.getenv("PRODUCTALIAS")

res = product_service.service.exists(
    Products=factory.type_GetInfo_In([f"Products/{productalias}"]),
)

print(res)
