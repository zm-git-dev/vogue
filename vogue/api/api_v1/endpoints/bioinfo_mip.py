#!/usr/bin/env python
from typing import List


from vogue.settings import templates

from vogue.adapter import VogueAdapter
from vogue.settings import get_vogue_adapter
from fastapi import APIRouter, Depends, Request

router = APIRouter()
from vogue.constants.constants import YEARS, BIOINFO_HELP_URLS, DNA_PICARD, MONTHS, THIS_YEAR
from vogue.crud.find_plots.bioinfo.qc import qc_dna_picard_plot, qc_dna_picard_time_plot
from vogue import __version__


@router.get("/Bioinfo/picard_time")
async def qc_dna_picard_time(
    request: Request,
    picard_metric: str = "PICARD_INSERT_SIZE MEAN_INSERT_SIZE",
    year: int = THIS_YEAR,
    adapter: VogueAdapter = Depends(get_vogue_adapter),
):
    qc_dna_results: List[dict] = qc_dna_picard_time_plot(adapter, year)
    selected_group, selcted_metric = picard_metric.split()
    return templates.TemplateResponse(
        "qc_over_time.html",
        context=dict(
            request=request,
            selected_group=selected_group,
            selcted_metric=selcted_metric,
            qc_dna_results=qc_dna_results,
            DNA_PICARD=DNA_PICARD,
            help_urls=BIOINFO_HELP_URLS,
            months=[m[1] for m in MONTHS],
            header="QC over time",
            version=__version__,
            year_of_interest=year,
            years=YEARS,
        ),
    )


@router.get(
    "/Bioinfo/picard",
)
async def qc_dna_picard(
    request: Request,
    Y_axis: str = "PICARD_INSERT_SIZE MEAN_INSERT_SIZE",
    X_axis: str = "PICARD_INSERT_SIZE MEAN_INSERT_SIZE",
    year: int = THIS_YEAR,
    adapter: VogueAdapter = Depends(get_vogue_adapter),
):
    qc_dna_results: List[dict] = qc_dna_picard_plot(adapter, year)
    Y_group, Y_axis = Y_axis.split()
    X_group, X_axis = X_axis.split()
    return templates.TemplateResponse(
        "qc_dna_picard.html",
        context=dict(
            request=request,
            Y_axis=Y_axis,
            X_axis=X_axis,
            groups=list(set([Y_group, X_group])),
            qc_dna_results=qc_dna_results,
            DNA_PICARD=DNA_PICARD,
            help_urls=BIOINFO_HELP_URLS,
            header="QC plots",
            version=__version__,
            year_of_interest=year,
            years=YEARS,
        ),
    )
