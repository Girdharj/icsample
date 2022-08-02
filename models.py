from typing import Optional
from pydantic import BaseModel

class SampleIC(BaseModel):
    sampleId: Optional[str] = None
    bridgeIc: Optional[int] = None
    bridgeWidth: Optional[int] = None
    fullWidthIc: Optional[int] = None
    average: Optional[int] = None

class PFMdata(BaseModel):
    PFM_average: Optional[int] = None