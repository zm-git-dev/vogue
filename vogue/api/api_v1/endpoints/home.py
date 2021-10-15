#!/usr/bin/env python
from pydantic import BaseModel

from vogue.constants.constants import MONTHS, YEARS, THIS_YEAR
from vogue.crud.find_plots.home import home_samples, home_customers
from vogue import __version__


from vogue.adapter import VogueAdapter
from vogue.settings import get_vogue_adapter, templates

from fastapi import APIRouter, Depends, Request

router = APIRouter()


@router.get("/home")
async def home(
    request: Request,
    adapter: VogueAdapter = Depends(get_vogue_adapter),
    year: int = THIS_YEAR,
    month: int = 0,
):

    sample_series, cathegories = home_samples(adapter, int(year), month)
    customers = home_customers(adapter, int(year), month)
    return templates.TemplateResponse(
        "index.html",
        context={
            "request": request,
            "version": __version__,
            "sample_series": sample_series,
            "cathegories": cathegories,
            "customers": customers,
            "year_of_interest": year,
            "month_of_interest": month,
            "months": MONTHS,
            "month_name": MONTHS[month - 1][1] if month else "",
            "years": YEARS,
        },
    )
