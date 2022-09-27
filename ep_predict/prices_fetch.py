
import io
import requests


def fetch_agile_outgoing():
    """Import the agile outgoing dataset fixing the datetime to a naive string"""
    stats_url = "https://www.energy-stats.uk/wp-content/historic-data/csv_agileoutgoing_J_South_Eastern_England.csv"
    data = requests.get(stats_url, stream=True)
    content = io.StringIO()
    data.raise_for_status()
    for chunk in data.iter_content(chunk_size=128):
        content.write(chunk.decode("utf-8"))
    content.seek(0)
    return content
