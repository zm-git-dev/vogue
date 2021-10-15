#!/usr/bin/env python


from vogue.settings import templates

from vogue.adapter import VogueAdapter
from vogue.settings import get_vogue_adapter
from fastapi import APIRouter, Depends, Request

router = APIRouter()


from vogue.constants.constants import LANE_UDFS, YEARS, THIS_YEAR
from vogue.crud.find_plots.sequencing import instrument_info
from vogue import __version__


@router.get("/sequencing/runs")
async def runs(
    request: Request,
    metric: str = "% Bases >=Q30",
    year: int = THIS_YEAR,
    adapter: VogueAdapter = Depends(get_vogue_adapter),
):

    print(metric)
    selcted_metric = metric
    aggregate_result = instrument_info(adapter, year, selcted_metric)

    return templates.TemplateResponse(
        "runs.html",
        context=dict(
            request=request,
            header="Sequencing Instruments",
            page_id="runs",
            metric=selcted_metric,
            metrices=LANE_UDFS,
            results=aggregate_result,
            version=__version__,
            year_of_interest=year,
            years=YEARS,
        ),
    )
