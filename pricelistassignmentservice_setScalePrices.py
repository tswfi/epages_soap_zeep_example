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
factory1 = pricelistassignment_service.zeep.type_factory("ns1")

#pricelistassignment_service.zeep.wsdl.dump()

productalias = os.getenv("PRODUCTALIAS")
productalias2 = os.getenv("PRODUCTALIAS2")
pricelistalias = os.getenv("PRICELISTALIAS")

res = pricelistassignment_service.service.setScalePrices(
    Products=factory.type_SetScalePrices_In([
        factory1.TSetScalePrices_Input(
            Product=f"Products/{productalias}",
            PriceList=f"PriceLists/{pricelistalias}",
            ScalePrices=factory1.ListOfScalePrices([
                factory1.TScalePrice(
                    Quantity=5.0,
                    Price=80.0
                ),
                factory1.TScalePrice(
                    Quantity=10.0,
                    Price=55.0
                ),
            ])),
        factory1.TSetScalePrices_Input(
            Product=f"Products/{productalias2}",
            PriceList=f"PriceLists/{pricelistalias}",
            ScalePrices=factory1.ListOfScalePrices([
                factory1.TScalePrice(
                    Quantity=15.0,
                    Price=321.0
                ),
                factory1.TScalePrice(
                    Quantity=20.0,
                    Price=123.0
                ),
            ]))
    ])
)

print(res)
