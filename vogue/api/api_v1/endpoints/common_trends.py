#!/usr/bin/env python

from vogue.constants.constants import MONTHS, YEARS, THIS_YEAR
from vogue.crud.find_plots.metric_per_month import value_per_month
from vogue import __version__
from vogue.settings import templates

from vogue.adapter import VogueAdapter
from vogue.settings import get_vogue_adapter
from fastapi import APIRouter, Depends, Request

router = APIRouter()


@router.get("/common/turn_around_times")
def turn_around_times(
    request: Request, year: int = THIS_YEAR, adapter: VogueAdapter = Depends(get_vogue_adapter)
):

    y_vals = [
        "received_to_delivered",
        "received_to_prepped",
        "prepped_to_sequenced",
        "sequenced_to_delivered",
    ]
    results_grouped_by_prio = {}
    results_grouped_by_cat = {}
    for y_val in y_vals:
        results_grouped_by_prio[y_val] = value_per_month(
            adapter=adapter, year=year, y_val=y_val, group_key="priority"
        )
        results_grouped_by_cat[y_val] = value_per_month(
            adapter=adapter, year=year, y_val=y_val, group_key="category"
        )

    return templates.TemplateResponse(
        "turn_around_times.html",
        context=dict(
            request=request,
            header="Turnaround Times",
            page_id="turn_around_times",
            data_prio=results_grouped_by_prio,
            data_cat=results_grouped_by_cat,
            months=[m[1] for m in MONTHS],
            version=__version__,
            year_of_interest=year,
            years=YEARS,
        ),
    )


@router.get("/common/samples")
def common_samples(
    request: Request, year: int = THIS_YEAR, adapter: VogueAdapter = Depends(get_vogue_adapter)
):
    data_cat = value_per_month(adapter=adapter, year=year, y_val="count", group_key="category")
    data_prio = value_per_month(adapter=adapter, year=year, y_val="count", group_key="priority")
    return templates.TemplateResponse(
        "samples.html",
        context=dict(
            request=request,
            header="Samples",
            page_id="samples",
            data_prio=data_prio,
            data_cat=data_cat,
            months=[m[1] for m in MONTHS],
            version=__version__,
            year_of_interest=year,
            years=YEARS,
        ),
    )
