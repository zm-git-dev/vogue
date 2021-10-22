from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from vogue.adapter import VogueAdapter
from vogue.crud.create import create_sample, create_bioinfo_sample
from vogue.exceptions import InsertError
from vogue.models.database import Sample, BioInfoSample
from vogue.settings import get_vogue_adapter
from vogue.tools.auth import verify_signature

router = APIRouter()


@router.post("/sample", response_model=Sample)
def sample(
    request: Request, database_sample: Sample, adapter: VogueAdapter = Depends(get_vogue_adapter)
):
    verify_signature(request=request)

    try:
        inserted_id = create_sample(adapter=adapter, sample=database_sample)
    except InsertError as e:
        return JSONResponse(content=e.message)

    return JSONResponse(content=f"Sample {inserted_id} was just inserted to the sample collection")


@router.post("/bioinfo_sample", response_model=BioInfoSample)
def bioinfo_sample(
    request: Request,
    database_sample: BioInfoSample,
    adapter: VogueAdapter = Depends(get_vogue_adapter),
):
    verify_signature(request=request)
    try:
        inserted_id = create_bioinfo_sample(adapter=adapter, sample=database_sample)
    except InsertError as e:
        return JSONResponse(content=e.message)

    return JSONResponse(
        content=f"Sample {inserted_id} was just inserted to the bioinfo_sample collection"
    )
