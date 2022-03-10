import random
from datetime import datetime
from typing import List

import numpy as np
from pydantic import BaseModel


class PriceInfo(BaseModel):
    buckets: List[str]
    bucket_values: List[int]

    def get_bucket_labels(self):
        labels = []
        for i in range(len(self.buckets) - 1):
            labels.append(f"${self.buckets[i]} - ${self.buckets[i+1]}")
        labels.append(f"${self.buckets[-1]}+")
        return labels


class AutoDataPoint(BaseModel):
    price: int

class AutoDataRepository:
    def fetch_data(self, start_year: int, end_year: int, make: str, model: str, date: datetime) -> List[AutoDataPoint]:
        raise NotImplementedError()

class MockAutoDataRepository(AutoDataRepository):
    def fetch_data(self, start_year: int, end_year: int, make: str, model: str, date: datetime) -> List[AutoDataPoint]:
        number_of_values = random.randint(5, 40)
        mean = random.randint(5000, 10000)
        dev = random.randint(1000, 3000)
        prices = np.random.normal(mean, dev, number_of_values)
        return [AutoDataPoint(price=int(p)) for p in prices]

def get_price_distribution(data_repo: AutoDataRepository, start_year: int, end_year: int, make: str, model: str, date: datetime) -> PriceInfo:
    NUMBER_OF_BUCKETS = 7

    # fetch all vehicles w/ Y/M/M
    # query only 6mo/1yr back
    # exclude any results where the price is < $100
    # bucket the values within the range
    data = data_repo.fetch_data(start_year, end_year, make, model, date)
    filtered_prices = [d.price for d in data if d.price > 100]
    raw_buckets = np.linspace(min(filtered_prices), max(filtered_prices), NUMBER_OF_BUCKETS)
    buckets = [int(b) for b in raw_buckets]
    bucket_values = [0] * NUMBER_OF_BUCKETS
    for price in filtered_prices:
        bucketed = False
        for i in range(NUMBER_OF_BUCKETS - 1):
            if price >= buckets[i] and price < buckets[i+1]:
                bucket_values[i] += 1
                bucketed = True
                break
        if not bucketed:
            bucket_values[-1] += 1
    
    info = PriceInfo(buckets=buckets, bucket_values=bucket_values)
    return info