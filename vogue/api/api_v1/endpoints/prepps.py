#!/usr/bin/env python

from vogue.settings import templates
from vogue.adapter import VogueAdapter
from vogue.settings import get_vogue_adapter
from fastapi import APIRouter, Depends, Request
from vogue.constants.constants import MONTHS, YEARS, THIS_YEAR
from vogue.crud.find_plots.metric_per_month import value_per_month
from vogue.crud.find_plots.prepps import find_concentration_defrosts, find_concentration_amount
from vogue import __version__

router = APIRouter()


@router.get("/prepps/microbial/")
async def microbial(
    request: Request,
    year: int = THIS_YEAR,
    adapter: VogueAdapter = Depends(get_vogue_adapter),
):
    data = value_per_month(adapter, year, "microbial_library_concentration", "strain")

    return templates.TemplateResponse(
        "microbial.html",
        context=dict(
            request=request,
            header="Microbial Samples",
            data=data,
            months=[m[1] for m in MONTHS],
            version=__version__,
            year_of_interest=year,
            years=YEARS,
        ),
    )


@router.get("/prepps/target_enrichment")
async def target_enrichment(
    request: Request, year: int = THIS_YEAR, adapter: VogueAdapter = Depends(get_vogue_adapter)
):
    library_size_post_hyb = value_per_month(adapter, year, "library_size_post_hyb", "source")
    library_size_pre_hyb = value_per_month(adapter, year, "library_size_pre_hyb", "source")

    return templates.TemplateResponse(
        "target_enrichment.html",
        context=dict(
            request=request,
            header="Target Enrichment (exom/panels)",
            data_pre_hyb=library_size_pre_hyb,
            data_post_hyb=library_size_post_hyb,
            months=[m[1] for m in MONTHS],
            version=__version__,
            year_of_interest=year,
            years=YEARS,
        ),
    )


@router.get("/prepps/wgs")
async def wgs(
    request: Request, year: int = THIS_YEAR, adapter: VogueAdapter = Depends(get_vogue_adapter)
):
    concentration_time = value_per_month(adapter, year, "nr_defrosts-concentration")
    concentration_defrosts = find_concentration_defrosts(adapter=adapter, year=year)

    return templates.TemplateResponse(
        "wgs.html",
        context=dict(
            request=request,
            header="WGS illumina PCR-free",
            concentration_defrosts=concentration_defrosts,
            concentration_time=concentration_time,
            months=[m[1] for m in MONTHS],
            version=__version__,
            year_of_interest=year,
            years=YEARS,
        ),
    )


@router.get("/prepps/lucigen")
async def lucigen(
    request: Request, year: int = THIS_YEAR, adapter: VogueAdapter = Depends(get_vogue_adapter)
):
    amount_concentration_time = value_per_month(adapter, year, "amount-concentration")
    concentration_amount = find_concentration_amount(adapter=adapter, year=year)

    return templates.TemplateResponse(
        "lucigen.html",
        context=dict(
            request=request,
            header="Lucigen PCR-free",
            amount_concentration_time=amount_concentration_time,
            months=[m[1] for m in MONTHS],
            amount=concentration_amount,
            version=__version__,
            year_of_interest=year,
            years=YEARS,
        ),
    )
