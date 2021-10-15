from typing import Optional

from pydantic import Field, BaseModel


class Sample(BaseModel):
    id: str = Field(..., alias="_id")
    sequenced_date: Optional[int]
    received_date: Optional[int]
    prepared_date: Optional[int]
    delivery_date: Optional[int]
    sequenced_to_delivered: Optional[int]
    prepped_to_sequenced: Optional[int]
    received_to_prepped: Optional[int]
    received_to_delivered: Optional[int]
    family: Optional[int]
    strain: Optional[str]
    source: Optional[int]
    customer: Optional[int]
    priority: Optional[int]
    initial_qc: Optional[int]
    library_qc: Optional[int]
    prep_method: Optional[str]
    sequencing_qc: Optional[int]
    application_tag: Optional[str]
    category: Optional[str]
    amount: Optional[float]
    amount_concentration: Optional[float]
    nr_defrosts: Optional[int]
    lotnr: Optional[str]
    microbial_library_concentration: Optional[float]
    library_size_pre_hyb: Optional[int]
    library_size_post_hyb: Optional[int]
    library_size_pre_hyb: Optional[int]
    library_size_post_hyb: Optional[int]

    class Config:
        allow_population_by_field_name = True
