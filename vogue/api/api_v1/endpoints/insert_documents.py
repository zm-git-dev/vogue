from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from vogue.adapter import VogueAdapter
from vogue.crud.create import create_sample, create_bioinfo_sample
from vogue.exceptions import InsertError
from vogue.models.database import Sample, BioInfoSample
from vogue.settings import get_vogue_adapter


router = APIRouter()


@router.post("/sample", response_model=Sample)
def sample(database_sample: Sample, adapter: VogueAdapter = Depends(get_vogue_adapter)):

    try:
        inserted_id = create_sample(adapter=adapter, sample=database_sample)
    except InsertError as e:
        return JSONResponse(content=e.message)

    return JSONResponse(content=f"sample {inserted_id} was just inserted to the sample collection")


@router.post("/bioinfo_sample", response_model=BioInfoSample)
def bioinfo_sample(
    database_sample: BioInfoSample, adapter: VogueAdapter = Depends(get_vogue_adapter)
):

    try:
        inserted_id = create_bioinfo_sample(adapter=adapter, sample=database_sample)
    except InsertError as e:
        return JSONResponse(content=e.message)

    return JSONResponse(content=f"sample {inserted_id} was just inserted to the bioinfo_sample")
