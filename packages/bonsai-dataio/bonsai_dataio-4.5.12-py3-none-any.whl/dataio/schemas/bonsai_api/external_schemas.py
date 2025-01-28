import datetime
from typing import Optional, ClassVar, Dict, Tuple

from pydantic import Field, PrivateAttr

import dataio.schemas.bonsai_api.PPF_fact_schemas_uncertainty as PPF_fact_schemas_uncertainty
from dataio.schemas.bonsai_api.base_models import FactBaseModel_uncertainty


class PRODCOMProductionVolume(PPF_fact_schemas_uncertainty.ProductionVolumes_uncertainty):
    indicator: str

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("prodcom", "location"),
        "product": ("prodcom_total_2_0", "flowobject"),
    }  # "product" could also be prodcom_sold_2_0 depending on context

    def __str__(self) -> str:
        return f"{self.location}-{self.product}-{self.activity}-{self.time}-{self.value}-{self.unit}"


class IndustrialCommodityStatistic(PPF_fact_schemas_uncertainty.ProductionVolumes_uncertainty):

    def __str__(self) -> str:
        return f"{self.location}-{self.product}-{self.activity}-{self.time}-{self.value}-{self.unit}"


class baseExternalSchemas(FactBaseModel_uncertainty):
    # Created with Sanders. Might Not be the base
    location: str
    time: int
    unit: str
    value: float
    comment: Optional[str] = None
    flag: Optional[str] = None


class ExternalMonetarySUT(baseExternalSchemas):
    table_type: str  # Supply or use table
    product_code: str
    product_name: str
    activity_code: str
    activity_name: str
    price_type: str = Field(  # Current price or previous year price.
        default="current prices"
    )
    consumer_price: bool = Field(default=False)  # Consumer price vs production price
    money_unit: Optional[str] = None  # Millions, billions etc.


# For annual data tables that start on a day other than January 1st. E.g. the fiscal year of India.
class BrokenYearMonetarySUT(ExternalMonetarySUT):
    time: datetime.date #Start date of fiscal year


class EuropeanMonetarySUT(ExternalMonetarySUT):
    _classification: ClassVar[Dict[str, Tuple[str, str]]] ={
        "product_code": ("cpa_2_1", "flowobject"),
        "activity_code": ("nace_rev2", "activitytype"),
    }


class OldEuropeanMonetarySUT(ExternalMonetarySUT):
    _classification: ClassVar[Dict[str, Tuple[str, str]]] ={
        "product_code": ("cpa_2008", "flowobject"),
        "activity_code": ("nace_rev2", "activitytype"),
    }


class OlderEuropeanMonetarySUT(ExternalMonetarySUT):
    _classification: ClassVar[Dict[str, Tuple[str, str]]] ={
        "product_code": ("cpa_2008", "flowobject"),
        "activity_code": ("nace_rev1_1", "activitytype"),
    }


class InternationalMonetarySUT(ExternalMonetarySUT):
    _classification: ClassVar[Dict[str, Tuple[str, str]]] ={
        "product_code": ("cpc_2_1", "flowobject"),
        "activity_code": ("isic_rev4", "activitytype"),
    }


class NACEMonetarySUT(ExternalMonetarySUT):
    _classification: ClassVar[Dict[str, Tuple[str, str]]] ={
        "product_code": ("nace_rev2", "flowobject"),
        "activity_code": ("nace_rev2", "activitytype"),
    }


class OECDMonetarySUT(ExternalMonetarySUT):
    _classification: ClassVar[Dict[str, Tuple[str, str]]] ={
        "product_code": ("cpa_2008", "flowobject"),
        "activity_code": ("isic_rev4", "activitytype"),
    }


class AustralianMonetarySUT(ExternalMonetarySUT):
    _classification: ClassVar[Dict[str, Tuple[str, str]]] ={
        "product_code": ("suic", "flowobject"),
        "activity_code": ("anzsic_2006", "activitytype"),
    }


class EgyptianMonetarySUT(BrokenYearMonetarySUT):
    _classification: ClassVar[Dict[str, Tuple[str, str]]] ={
        "product_code": ("cpc_1_1", "flowobject"),
        "activity_code": ("isic_rev4", "activitytype"),
    }


class IndianMonetarySUT(BrokenYearMonetarySUT):
    _classification: ClassVar[Dict[str, Tuple[str, str]]] ={
        "product_code": ("india_sut", "flowobject"),
        "activity_code": ("india_sut", "activitytype"),
    }


class JapanMonetarySUT(BrokenYearMonetarySUT):
    _classification: ClassVar[Dict[str, Tuple[str, str]]] ={
        "product_code": ("japan_sut", "flowobject"),
        "activity_code": ("japan_sut", "activitytype"),
    }


class FAOstat(FactBaseModel_uncertainty):
    product_name: str
    product: str
    fao_element: str
    location: str
    time: int
    value: float
    unit: str
    flag: Optional[str] = None

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("FAOcode", "location"),
        "product": ("faostat", "flowobject"),
    }


class FAOtrade(FactBaseModel_uncertainty):
    product_name: str
    product: str
    export_location: str  # Exporter
    import_location: str  # Importer
    time: int
    value: float
    unit: str
    flag: Optional[str] = None

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("fao_area", "location"),
        "partner": ("fao_area", "location"),
        "product": ("fao_items", "flowobject"),
    }


class UNdataEnergyBalance(FactBaseModel_uncertainty):
    activity: str
    product: str
    location: str
    time: int
    value: float
    unit: str
    comment: Optional[str] = None
    flag: Optional[str] = None

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("undata_energy", "location"),
        "product": ("undata_energy_stats", "flowobject"),  # or prodcom_sold_2_0
    }

    def __str__(self) -> str:
        return f"{self.location}-{self.product}-{self.activity}-{self.time}"


class UNdataEnergyStatistic(FactBaseModel_uncertainty):
    activity: str
    product: str
    location: str
    time: int
    value: float
    unit: str
    comment: Optional[str] = None
    flag: Optional[str] = None
    conversion_factor: Optional[float] = None

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("undata_energy", "location"),
        "product": ("undata_energy_stats", "flowobject"),
        "activity": ("undata_energy_stats", "activitytype"),
    }

    def __str__(self) -> str:
        return f"{self.location}-{self.product}-{self.activity}-{self.time}"


class BACITrade(FactBaseModel_uncertainty):
    time: int
    product: int
    export_location: str
    import_location: str
    value: float
    unit: str
    flag: Optional[str] = None

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "product": ("baci", "flowobject"),
        "export_location": ("baci", "location"),
        "import_location": ("baci", "location"),
    }


class USGSProductionVolume(PPF_fact_schemas_uncertainty.ProductionVolumes_uncertainty):

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("name_short", "location"),
        "product": ("usgs", "flowobject")
    }

    def __str__(self) -> str:
        return f"{self.location}-{self.product}-{self.activity}-{self.time}-{self.value}-{self.unit}"


class StatCanChemProductionVolume(PPF_fact_schemas_uncertainty.ProductionVolumes_uncertainty):

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        #TODO after Albert has created the correspondances
    }

    def __str__(self) -> str:
        return f"{self.location}-{self.product}-{self.activity}-{self.time}-{self.value}-{self.unit}"


class ComexTrade(FactBaseModel_uncertainty):
    time: int
    product: str
    activity: str
    export_location: str
    import_location: str
    value: float
    unit: str
    transport_mode: Optional[str] = None
    country_active_transport_mode: Optional[str] = None
    container: Optional[str] = None
    flag: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.product}-{self.activity}-{self.time}-{self.value}-{self.unit}"

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "product": ("comext", "flowobject"),
        "activity": ("comext", "activitytype"),
        "export_location": ("ISO2", "location"),
        "import_location": ("ISO2", "location"),
    }
