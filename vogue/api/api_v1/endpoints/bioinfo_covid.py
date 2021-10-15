#!/usr/bin/env python


from vogue.settings import templates

from vogue.adapter import VogueAdapter
from vogue.settings import get_vogue_adapter
from fastapi import APIRouter, Depends, Request

router = APIRouter()
from vogue.constants.constants import MICROSALT, YEARS, THIS_YEAR
from vogue.crud.find_plots.bioinfo.micro import microsalt_get_qc_time
from vogue.crud.find_plots.bioinfo.covid import get_qc
from vogue import __version__

HEADER = "Microsalt Covid"


@router.get(
    "/Bioinfo/Covid/qc_time",
)
async def covid_qc_time(
    request: Request,
    metric_path: str = "picard_markduplicate.insert_size",
    year: int = THIS_YEAR,
    adapter: VogueAdapter = Depends(get_vogue_adapter),
):
    """Box plot with qc data per month"""

    results = microsalt_get_qc_time(adapter, year=year, metric_path=metric_path, category="cov")
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
            header=HEADER,
            version=__version__,
            year_of_interest=year,
            MICROSALT=MICROSALT,
            years=YEARS,
        ),
    )


@router.get(
    "/Bioinfo/Covid/qc_time_scatter",
)
async def covid_qc_scatter(
    request: Request,
    metric_path: str = "picard_markduplicate.insert_size",
    year: int = THIS_YEAR,
    adapter: VogueAdapter = Depends(get_vogue_adapter),
):
    """Scatter plot with qc data over time, grouped by prep method"""

    results = get_qc(adapter, year=year, metric_path=metric_path)

    return templates.TemplateResponse(
        "cov_qc_scatter.html",
        context=dict(
            request=request,
            results=results,
            MICROSALT=MICROSALT,
            selected_group=metric_path.split(".")[0],
            metric=metric_path.split(".")[1],
            header=HEADER,
            version=__version__,
            year_of_interest=year,
            years=YEARS,
        ),
    )
