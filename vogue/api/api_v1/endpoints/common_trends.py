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

    results_grouped_by_prio = {
        "received_to_delivered": value_per_month(
            adapter=adapter, year=year, y_val="received_to_delivered", group_key="priority"
        ),
        "received_to_prepped": value_per_month(
            adapter=adapter,
            year=year,
            y_val="received_to_prepped",
            group_key="priority",
        ),
    }

    results_grouped_by_cat = {
        "received_to_delivered": value_per_month(
            adapter=adapter, year=year, y_val="received_to_delivered", group_key="category"
        ),
        "received_to_prepped": value_per_month(
            adapter=adapter,
            year=year,
            y_val="received_to_prepped",
            group_key="category",
        ),
    }
    results_grouped_by_cat["received_to_prepped"].pop("cov", None)
    results_grouped_by_cat["received_to_prepped"].pop("rml", None)
    results_grouped_by_cat["received_to_prepped"].pop("NA", None)
    results_grouped_by_prio["received_to_prepped"].pop("cov", None)
    results_grouped_by_prio["received_to_prepped"].pop("rml", None)
    results_grouped_by_prio["received_to_prepped"].pop("NA", None)

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
