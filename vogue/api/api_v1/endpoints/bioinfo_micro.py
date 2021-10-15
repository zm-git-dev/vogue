#!/usr/bin/env python
from typing import Optional

from vogue.settings import templates

from vogue.adapter import VogueAdapter
from vogue.settings import get_vogue_adapter
from fastapi import APIRouter, Depends, Request

router = APIRouter()

from vogue.constants.constants import YEARS, MICROSALT, THIS_YEAR
from vogue.crud.find_plots.bioinfo.micro import (
    microsalt_get_untyped,
    microsalt_get_st_time,
    microsalt_get_qc_time,
    microsalt_get_strain_st,
)
from vogue import __version__


@router.get("/Bioinfo/Microbial/strain_st")
async def micro_strain_st(
    request: Request,
    strain: Optional[str] = "",
    year: int = THIS_YEAR,
    adapter: VogueAdapter = Depends(get_vogue_adapter),
):
    results = microsalt_get_strain_st(adapter, year)
    if results and not strain:
        strain = list(results.keys())[0]
    return templates.TemplateResponse(
        "microsalt_strain_st.html",
        context=dict(
            request=request,
            data=results.get(strain, {}),
            strain=strain,
            categories=results.keys(),
            header="Microsalt",
            version=__version__,
            year_of_interest=year,
            years=YEARS,
        ),
    )


@router.get("/Bioinfo/Microbial/qc_time")
async def micro_qc_time(
    request: Request,
    metric_path: str = "picard_markduplicate.insert_size",
    year: int = THIS_YEAR,
    adapter: VogueAdapter = Depends(get_vogue_adapter),
):
    results = microsalt_get_qc_time(adapter, year=year, metric_path=metric_path, category="mic")

    return templates.TemplateResponse(
        "microsalt_qc_time.html",
        context=dict(
            request=request,
            results=results["data"],
            outliers=results["outliers"],
            categories=results["labels"],
            mean=results["mean"],
            selected_group=metric_path.split(".")[0],
            selected_metric=metric_path.split(".")[1],
            header="Microsalt",
            version=__version__,
            year_of_interest=year,
            MICROSALT=MICROSALT,
            years=YEARS,
        ),
    )


@router.get("/Bioinfo/Microbial/untyped")
def micro_untyped(
    request: Request,
    year: int = THIS_YEAR,
    adapter: VogueAdapter = Depends(get_vogue_adapter),
):
    results = microsalt_get_untyped(adapter, year)

    return templates.TemplateResponse(
        "microsalt_untyped.html",
        context=dict(
            request=request,
            results=results["data"],
            categories=results["labels"],
            header="Microsalt",
            version=__version__,
            year_of_interest=year,
            MICROSALT=MICROSALT,
            years=YEARS,
        ),
    )


@router.get(
    "/Bioinfo/Microbial/st_time",
)
async def micro_st_time(
    request: Request,
    strain: str = "",
    year: int = THIS_YEAR,
    adapter: VogueAdapter = Depends(get_vogue_adapter),
):
    results_all = microsalt_get_st_time(adapter, year)
    if results_all["data"] and not strain:
        strain = list(results_all["data"].keys())[0]
    strain_results = results_all["data"].get(strain, {})

    return templates.TemplateResponse(
        "microsalt_st_time.html",
        context=dict(
            request=request,
            results=strain_results,
            results_sorted_keys=sorted(strain_results.keys()),
            strain=strain,
            strains=results_all["data"].keys(),
            categories=results_all["labels"],
            header="Microsalt",
            version=__version__,
            year_of_interest=year,
            MICROSALT=MICROSALT,
            years=YEARS,
        ),
    )
