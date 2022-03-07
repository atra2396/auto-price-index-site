import datetime
import json
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


@app.get("/")
def home(request: Request, year: Optional[int] = None, make: Optional[str] = None, model: Optional[str] = None):

    if year and make and model:
        buckets, bucket_vals = get_chart_data(year, make, model)
    else:
        buckets = bucket_vals = None

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "prices.html",
            {
                "request": request,
                "buckets": buckets,
                "values": bucket_vals,
                "year": year,
                "make": make,
                "model": model
            }
        )

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "years": list(YMM.keys()),
            "year": year,
            "make": make,
            "model": model,
            "buckets": buckets,
            "values": bucket_vals
        }
    )


@app.get("/api/years")
def get_years():
    return list(YMM.keys())


@app.get("/api/years/{year}/makes")
def get_makes(year: int):
    return list(YMM[str(year)].keys())


@app.get("/api/years/{year}/makes/{make}/models")
def get_models(year: int, make: str):
    return YMM[str(year)][make]

# ------


@app.get("/makes")
def makes_partial(request: Request, year: int = 2000):
    return templates.TemplateResponse("make-select.html", {"request": request, "makes": list(YMM[str(year)].keys()), "year": year})


@app.get("/models")
def models_partial(request: Request, year: int = 2000, make: str = ""):
    return templates.TemplateResponse("model-select.html", {"request": request, "models": list(YMM[str(year)][make])})


def get_chart_data(year, make, model):
    prices = get_price_distribution(AzureAutoDataRepository(), year, make, model, datetime.datetime.now())
    return prices.get_bucket_labels(), prices.bucket_values
