#!/usr/bin/env python

from vogue.constants.constants import THIS_YEAR
from vogue import __version__
from vogue.settings import templates

from vogue.adapter import VogueAdapter
from vogue.settings import get_vogue_adapter
from fastapi import APIRouter, Depends, Request
from vogue.crud.find_plots.genotype import get_genotype_plate

router = APIRouter()


@router.get("/Bioinfo/Genotype/plate")
async def genotype_plate(
    request: Request,
    plate_id: str = "ID81",
    year: int = THIS_YEAR,
    adapter: VogueAdapter = Depends(get_vogue_adapter),
):

    plot_data = get_genotype_plate(adapter, plate_id=plate_id)
    plot_data["plates"].sort()
    return templates.TemplateResponse(
        "genotype_plate.html",
        context=dict(
            request=request,
            plate_data=plot_data["data"],
            x_labels=plot_data["x_labels"],
            y_labels=plot_data["y_labels"],
            year_of_interest=year,
            header="Genotype",
            page_id="genotype_plate",
            version=__version__,
            plate_id=plot_data["plate_id"],
            plates=plot_data["plates"],
        ),
    )
