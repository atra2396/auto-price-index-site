import json
import os
from storage import get_table

if "DEV_MODE" in os.environ:
    with open("local.settings.json", "r") as s:
        settings = json.load(s)
    for key in settings.keys():
        os.environ[key] = settings[key]

def generate_ymm():
    LOCATIONS = ["lex", "louisville", "cincinnati", "indianapolis", "atlanta", "stlouis", "chicago", "charlotte"]
    table = get_table()
    partition_queries = [f"PartitionKey eq '{loc}'" for loc in LOCATIONS]
    partition_query = " or ".join(partition_queries)
    
    results = table.query_entities(partition_query)
    YMM = {}

    for result in results:
        year = result["year"]
        make = result["make"]
        model = result["model"]
        if year not in YMM:
            YMM[year] = {}
        
        if make not in YMM[year]:
            YMM[year][make] = []
        
        if model not in YMM[year][make]:
            YMM[year][make].append(model)
    
    with open("YMM.json", "x") as f:
        json.dump(YMM, f)