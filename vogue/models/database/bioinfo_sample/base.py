from typing import Optional

from pydantic import BaseModel, Field


class BioInfoSample(BaseModel):
    sample_id: str
    case_id: Optional[str]
