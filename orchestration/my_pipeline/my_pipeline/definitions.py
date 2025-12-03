import os
from dagster import Definitions, load_assets_from_modules
from dagster_dbt import DbtCliResource
from . import assets
from . import sensors 

all_assets = load_assets_from_modules([assets])
dbt_project_dir = os.fspath(assets.dbt_project.project_dir)

defs = Definitions(
    assets=all_assets,
    sensors=[sensors.email_failure_sensor], 
    resources={
        "dbt": DbtCliResource(project_dir=dbt_project_dir),
    },
)