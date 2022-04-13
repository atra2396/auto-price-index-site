import datetime
import json
import os
from typing import Optional

import jinja_partials
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from stats import get_price_distribution, MockAutoDataRepository
from storage import AzureAutoDataRepository

app = FastAPI()
templates = Jinja2Templates(directory="templates")
jinja_partials.register_starlette_extensions(templates)
app.mount("/static", StaticFiles(directory="static"), name="static")

with open("vehicles.json", "r") as f:
    YMM = json.load(f)

if "DEV_MODE" in os.environ:
    with open("local.settings.json", "r") as s:
        settings = json.load(s)
    for key in settings.keys():
        os.environ[key] = settings[key]

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("favicon.ico")

@app.get("/")
async def home(request: Request, start_year: Optional[int] = None, end_year: Optional[int] = None, make: Optional[str] = None, model: Optional[str] = None):

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

@app.get("/api/vehicles")
async def get_vehicle_data(request: Request):
    return YMM


def get_chart_data(start_year, end_year, make, model):

    if os.environ.get("STORAGE_CONNECTION_STRING"):
        repo = AzureAutoDataRepository()
    else:
        print("WARNING: No storage connection string detected. Serving mock data.")
        repo = MockAutoDataRepository()

    prices = get_price_distribution(repo, start_year, end_year, make, model, datetime.datetime.now())
    return prices.get_bucket_labels(), prices.bucket_values
