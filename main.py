import datetime
import json
import os
from typing import Optional

import jinja_partials
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from stats import get_price_distribution, MockAutoDataRepository
from storage import AzureAutoDataRepository

app = FastAPI()
templates = Jinja2Templates(directory="templates")
jinja_partials.register_starlette_extensions(templates)

with open("vehicles.json", "r") as f:
    YMM = json.load(f)

if "DEV_MODE" in os.environ:
    with open("local.settings.json", "r") as s:
        settings = json.load(s)
    for key in settings.keys():
        os.environ[key] = settings[key]

@app.get("/")
def home(request: Request, start_year: Optional[int] = None, end_year: Optional[int] = None, make: Optional[str] = None, model: Optional[str] = None):

    if start_year and end_year and make and model:
        buckets, bucket_vals = get_chart_data(start_year, end_year, make, model)
    else:
        buckets = bucket_vals = None

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "prices.html",
            {
                "request": request,
                "buckets": buckets,
                "values": bucket_vals,
                "start_year": start_year,
                "end_year": end_year,
                "make": make,
                "model": model
            }
        )

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "years": list(YMM.keys()),
            "start_year": start_year,
            "end_year": end_year,
            "make": make,
            "model": model,
            "buckets": buckets,
            "values": bucket_vals
        }
    )

# ------

@app.get("/end_years")
def end_years_partial(request: Request, start_year: int):
    return templates.TemplateResponse("end-year-select.html", {"request": request, "years": [int(y) for y in YMM.keys() if int(y) >= start_year]})

@app.get("/makes")
def makes_partial(request: Request, start_year: int, end_year: int):
    years = range(start_year, end_year+1)
    makes = [YMM.get(str(year)).keys() for year in years if YMM.get(str(year))]
    all_makes = []
    for make_list in makes:
        all_makes.extend(make_list)
    return templates.TemplateResponse("make-select.html", {"request": request, "makes": sorted(set(all_makes)), "start_year": start_year, "end_year": end_year})


@app.get("/models")
def models_partial(request: Request, start_year: int, end_year:int, make: str):
    years = range(start_year, end_year+1)
    models = [YMM[str(year)][make] for year in years if YMM.get(str(year), {}).get(make)]
    all_models = []
    for model_list in models:
        all_models.extend(model_list)

    return templates.TemplateResponse("model-select.html", {"request": request, "models": sorted(set(all_models))})


def get_chart_data(start_year, end_year, make, model):

    if os.environ.get("STORAGE_CONNECTION_STRING"):
        repo = AzureAutoDataRepository()
    else:
        print("WARNING: No storage connection string detected. Serving mock data.")
        repo = MockAutoDataRepository()

    prices = get_price_distribution(repo, start_year, end_year, make, model, datetime.datetime.now())
    return prices.get_bucket_labels(), prices.bucket_values
