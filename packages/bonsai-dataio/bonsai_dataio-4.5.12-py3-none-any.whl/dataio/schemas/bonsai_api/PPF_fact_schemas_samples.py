from typing import Optional

from pydantic import Field

import dataio.schemas.bonsai_api.facts as schemas
from dataio.schemas.bonsai_api.base_models import FactBaseModel_samples
from dataio.tools import BonsaiTableModel


class Use_samples(FactBaseModel_samples):
    location: str
    product: str
    activity: str
    unit: str
    value: float
    associated_product: Optional[str] = None
    flag: Optional[str] = (
        None  # TODO flag rework. Can be uncertainty, can be other. Different meanings across data sources.
    )
    time: int
    product_origin: Optional[str] = None  # Where the used product comes from.
    product_type: str = Field(
        default="use"
    )  # set automatically based on what data class is used

    def __str__(self) -> str:
        return f"{self.location}-{self.product}-{self.product_type}-{self.activity}-{self.time}-{self.value}-{self.unit}"


class Supply_samples(FactBaseModel_samples):
    location: str
    product: str
    activity: str
    unit: str
    value: float
    product_destination: Optional[str] = None
    associated_product: Optional[str] = None
    flag: Optional[str] = (
        None  # TODO flag rework. Can be uncertainty, can be other. Different meanings across data sources.
    )
    time: int
    product_type: str = Field(
        default="supply"
    )  # set automatically based on what data class is used. This can also be joint or combined product, but maybe needs to be a different attribute?

    def __str__(self) -> str:
        return f"{self.location}-{self.product}-{self.product_type}-{self.activity}-{self.time}-{self.value}-{self.unit}"


class Imports_samples(FactBaseModel_samples):
    location: str
    product: str
    product_origin: str  # Where the product comes from
    unit: str
    value: float
    time: int


class Valuation_samples(FactBaseModel_samples):
    location: str
    product: str
    valuation: str
    unit: str
    value: float
    time: int


class FinalUses_samples(FactBaseModel_samples):
    location: str
    product: str
    final_user: str  # Final use ctivity that uses the product
    unit: str
    value: float
    time: int


class SUTAdjustments_samples(FactBaseModel_samples):
    location: str
    adjustment: str
    product: Optional[str] = None
    product_origin: Optional[str] = None  # Where the product comes from
    final_user: Optional[str] = None  # Where the product is used
    unit: str
    value: float
    time: int


class OutputTotals_samples(FactBaseModel_samples):
    location: str
    activity: str
    output_compartment: str  # Where the outputs are used
    unit: str
    value: float
    time: int


class ValueAdded_samples(FactBaseModel_samples):
    location: str
    activity: str
    value_added_component: str  # Component of value added
    unit: str
    value: float
    time: int


class SocialSatellite_samples(FactBaseModel_samples):
    location: str
    activity: str
    social_flow: str  # Type of social flow
    unit: str
    value: float
    time: int


class ProductionVolumes_samples(FactBaseModel_samples):
    location: str
    product: str
    activity: Optional[str] = None
    unit: str
    value: float
    flag: Optional[str] = None  # TODO flag rework
    time: int
    inventory_time: Optional[int] = None
    source: str
    comment: Optional[str] = None
    monetary_unit: Optional[str]= None
    monetary_value: Optional[float]= None
    price_type: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.location}-{self.product}-{self.activity}-{self.time}-{self.value}-{self.unit}"


class Emissions_samples(FactBaseModel_samples):
    time: int
    year_emission: Optional[int] = (
        None  # TODO Rework into how we want to handle delayed emissions
    )
    location: str
    activity: str
    activity_unit: str
    emission_substance: str
    compartment: str  # location of emission, such as "Emission to air"
    product: str
    product_unit: str
    value: float
    unit: str
    flag: Optional[str] = None

    elementary_type: str = Field(
        default="emission"
    )

    def __str__(self) -> str:
        return f"{self.location}-{self.emission_substance}-{self.activity}-{self.activity_unit}-{self.time}-{self.value}-{self.unit}"


class TransferCoefficient_samples(FactBaseModel_samples):  # Similar to use
    location: Optional[str] = None
    output: str
    input_product: str
    activity: str
    coefficient_value: float
    unit: str
    flag: Optional[str] = (
        None  # TODO flag rework. Can be uncertainty, can be other. Different meanings across data sources.
    )
    time: Optional[int] = None
    transfer_type: str  #Should be one of these three value: "product", "emission" or "waste" TODO Validator
    

    def __str__(self) -> str:
        return f"{self.location}-{self.product}-{self.activity}-{self.time}-{self.coefficient_value}"


class Resource_samples(Emissions_samples):
    def __init__(self, **data):
        super().__init__(**data)
        self.elementary_type = "resource"


class PackagingData_samples(Supply_samples):
    def __init__(self, **data):
        super().__init__(**data)
        self.product_type = "packaging_data"


class WasteUse_samples(Use_samples):
    waste_fraction: bool

    def __init__(self, **data):
        super().__init__(**data)
        self.product_type = "waste_use"


class WasteSupply_samples(Supply_samples):
    waste_fraction: bool

    def __init__(self, **data):
        super().__init__(**data)
        self.product_type = "waste_supply"


class PropertyOfProducts_samples(FactBaseModel_samples):
    location: Optional[str] = None
    product: str
    value: float
    activity: Optional[str] = None
    unit: str
    description: Optional[str] = None


class Trade_samples(FactBaseModel_samples):
    time: int
    product: str
    export_location: str
    import_location: str
    value: float
    unit: str
    flag: Optional[str] = None  # TODO flag rework
    monetary_unit: Optional[str]= None
    monetary_value: Optional[float]= None
    price_type: Optional[str] = None