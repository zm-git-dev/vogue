from pathlib import Path
from typing import Optional

from genologics.lims import Lims
from pymongo import MongoClient
from pydantic import BaseSettings

from vogue.adapter import VogueAdapter

VOGUE_PACKAGE = Path(__file__).parent
PACKAGE_ROOT: Path = VOGUE_PACKAGE.parent
ENV_FILE: Path = PACKAGE_ROOT / ".env"
from fastapi.templating import Jinja2Templates

TEMPLATES_DIR: Path = VOGUE_PACKAGE / "api" / "api_v1" / "templates"
from fastapi.staticfiles import StaticFiles

STATIC_FILES: Path = VOGUE_PACKAGE / "api" / "api_v1" / "static"
static_files = StaticFiles(directory=str(STATIC_FILES))

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


class Settings(BaseSettings):
    """Settings for serving the vogue app and connect to the mongo database"""

    lims_base_uri: str = "dummy"
    lims_username: str = "dummy"
    lims_password: str = "dummy"
    db_uri: str = "mongodb://localhost:27017/vogue-demo"
    db_name: str = "vogue-demo"
    secret_key: str = "dummy"
    algorithm: str = "ABC"
    host: str = "localhost"
    access_token_expire_minutes: int = 60
    port: int = 8000

    class Config:
        env_file = str(ENV_FILE)


settings = Settings()


def get_lims() -> Lims:
    """Temporarily untill we have load from arnold in place """
    return Lims(settings.lims_base_uri, settings.lims_username, settings.lims_password)


def get_vogue_adapter():
    client = MongoClient(settings.db_uri)
    return VogueAdapter(client, db_name=settings.db_name)
