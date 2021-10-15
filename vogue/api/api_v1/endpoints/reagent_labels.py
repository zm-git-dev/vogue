#!/usr/bin/env python


from vogue.adapter import VogueAdapter
from vogue.settings import get_vogue_adapter, templates

from fastapi import APIRouter, Depends, Request

router = APIRouter()

from vogue.constants.constants import THIS_YEAR
from vogue.crud.find_plots.reagent_labels import reagent_label_data, reagent_category_data
from vogue import __version__

flowcell_performance_treshold = 0.3


@router.get("/reagent_labels")
async def reagent_labels(
    request: Request,
    index_category: str = "Illumina IDT UD",
    year: int = THIS_YEAR,
    adapter: VogueAdapter = Depends(get_vogue_adapter),
):

    aggregate_result = reagent_category_data(adapter, index_category, flowcell_performance_treshold)
    return templates.TemplateResponse(
        "reagent_labels.html",
        context=dict(
            request=request,
            flowcell_performance_treshold=flowcell_performance_treshold,
            header="Overall performance per index",
            nr_indexes=len(aggregate_result),
            index_category=index_category,
            index_categories=adapter.get_reagent_label_categories(),
            year_of_interest=year,
            results=aggregate_result,
            version=__version__,
        ),
    )


@router.get("/reagent_label")
async def reagent_label(
    request: Request,
    reagent_label: str = "G09 - UDI0071,Illumina IDT UD",
    year: int = THIS_YEAR,
    adapter: VogueAdapter = Depends(get_vogue_adapter),
):
    label, index_category = reagent_label.split(",")

    aggregate_result = reagent_label_data(adapter, label, flowcell_performance_treshold)
    index_categories = list(adapter.get_all_reagent_label_names_grouped_by_category())
    return templates.TemplateResponse(
        "reagent_label.html",
        context=dict(
            request=request,
            flowcell_performance_treshold=flowcell_performance_treshold,
            header="Normalized index performance per flowcell",
            index_category=index_category,
            year_of_interest=year,
            reagent_label=label,
            index_categories=index_categories,
            results=aggregate_result,
            version=__version__,
        ),
    )
