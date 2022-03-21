import datetime
import os
from typing import List

from azure.data.tables import TableServiceClient

from stats import AutoDataPoint, AutoDataRepository


def get_table():
    tsc = TableServiceClient.from_connection_string(
        os.environ["STORAGE_CONNECTION_STRING"]
    )
    return tsc.get_table_client(os.environ["DATA_TABLE_NAME"])

class AzureAutoDataRepository(AutoDataRepository):

    LOCATIONS = ["lex", "louisville", "cincinnati", "indianapolis", "atlanta", "stlouis", "chicago", "charlotte"]

    def fetch_data(self, start_year: int, end_year: int, make: str, model: str, date: datetime) -> List[AutoDataPoint]:
        table = get_table()
        partition_queries = [f"PartitionKey eq '{loc}'" for loc in self.LOCATIONS]
        partition_query = " or ".join(partition_queries)
        
        query = f"({partition_query}) and year ge {start_year} and year le {end_year} and make eq '{make}' and model eq '{model}'"
        result = table.query_entities(query)

        prices = [AutoDataPoint(price=r["price"]) for r in result]
        return prices