"""
Fetch historical and up to date wind and demand forecasts from National Grid

Use a polynomial chain curve fit to fill in the gaps on the demand forecasts

https://stackoverflow.com/questions/12935098/how-to-plot-line-polygonal-chain-with-numpy-scipy-matplotlib-with-minimal-smoo/12936696#12936696
"""

import io
import requests



def fetch_from_eso(resource):
    if resource == "historic-day-ahead-demand-forecast":
        url = "https://data.nationalgrideso.com/backend/dataset/8fbc8a09-06af-4c90-886f-d3025d38a349/resource/9847e7bb-986e-49be-8138-717b25933fbb/download/archive_1dayahead.csv"
    elif resource == "historic-day-ahead-wind-forecast":
        url = "https://data.nationalgrideso.com/backend/dataset/fbe3701d-1487-443e-abe9-47a6c01ecce2/resource/7524ec65-f782-4258-aaf8-5b926c17b966/download/archive_1dayaheadwind.csv"
    elif resource == "historic-7day-ahead-forecast":
        url = "https://api.nationalgrideso.com/dataset/2b90a483-f59d-455b-be6d-3cb4c13a85d0/resource/6f7408b4-47fd-4ae7-b1e5-f095a3a5a2dc/download/archive_7dayahead.csv"
    elif resource =="14-day-wind":
        url = "https://data.nationalgrideso.com/backend/dataset/2f134a4e-92e5-43b8-96c3-0dd7d92fcc52/resource/93c3048e-1dab-4057-a2a9-417540583929/download/14da_wind_forecast.csv"
    data = requests.get(url, stream=True)
    content = io.StringIO()
    data.raise_for_status()
    for chunk in data.iter_content(chunk_size=128):
        content.write(chunk.decode("utf-8"))
    content.seek(0)
    return content


def fetch_wind_forecast():
    """
    Fetch the wind forecast in a dataframe
    """
    return fetch_from_eso("historic-day-ahead-wind-forecast"), fetch_from_eso("14-day-wind")


def fetch_demand_forecast():
    return fetch_from_eso("historic-day-ahead-demand-forecast"), fetch_from_eso("historic-7day-ahead-forecast")
