from fastapi import FastAPI

from vogue.api.api_v1.endpoints import (
    insert_documents,
    home,
    common_trends,
    sequencing,
    genootype,
    reagent_labels,
    prepps,
    bioinfo_covid,
    bioinfo_micro,
    bioinfo_mip,
    update,
)
from vogue.settings import static_files


app = FastAPI()
app.mount(
    "/static",
    static_files,
    name="static",
)

app.include_router(home.router, tags=["home"])
app.include_router(common_trends.router, tags=["common_trends"])
app.include_router(sequencing.router, tags=["sequencing"])
app.include_router(genootype.router, tags=["genotype"])
app.include_router(reagent_labels.router, tags=["index"])
app.include_router(prepps.router, tags=["preps"])
app.include_router(bioinfo_micro.router, tags=["bioinfo_micro"])
app.include_router(bioinfo_covid.router, tags=["bioinfo_covid"])
app.include_router(bioinfo_mip.router, tags=["bioinfo_mip"])
app.include_router(update.router, tags=["update"])
app.include_router(insert_documents.router, tags=["sample"])
