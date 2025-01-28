from typing import Optional

from dataio.schemas.bonsai_api.base_models import FactBaseModel_uncertainty
from dataio.schemas.bonsai_api.uncertainty import Uncertainty


class Parameters(FactBaseModel_uncertainty):
    time: int = None
    location: str = None
    activity: str = None
    product: str = None
    flexible_category: Optional[dict] = None
    value: float
    unit: str
    source: str
    flag: Optional[str] = None  # TODO flag rework
    description: str

    def __str__(self) -> str:
        return f"{self.location}-{self.product}-{self.activity}-{self.time}-{self.value}-{self.unit}"


import dataio.schemas.bonsai_api.ipcc as schemas

schemas.Parameters.names.location
