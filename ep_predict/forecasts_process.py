import datetime
import time
import zoneinfo

import pandas as pd
from scipy.interpolate import pchip

from ep_predict import utils

def build_date(date_string):
    if date_string.endswith("2400"):
        output = datetime.datetime.strptime(
            date_string, "%Y-%m-%dT00:00:00Z 2400"
        ) + datetime.timedelta(days=1)
    else:
        output = datetime.datetime.strptime(date_string, "%Y-%m-%dT00:00:00Z %H%M")
    tz = zoneinfo.ZoneInfo("Europe/London")
    with_tz = output.replace(tzinfo=tz)
    return with_tz.astimezone(datetime.timezone.utc)



def build_demand_forecast_interpolator(response, future_response):
    results_old = pd.read_csv(
        response
    )
    future_results = pd.read_csv(
        future_response
    )
    results = pd.concat([results_old, future_results], ignore_index=True)
    results = results[["TARGETDATE", "CP_ST_TIME", "CP_END_TIME", "FORECASTDEMAND"]]
    result_start = results.drop(["CP_END_TIME"], inplace=False, axis=1)
    result_start["TIME"] = result_start.CP_ST_TIME.astype(str).str.zfill(4)
    result_end = results.drop(["CP_ST_TIME"], inplace=False, axis=1)
    result_end["TIME"] = result_end.CP_END_TIME.astype(str).str.zfill(4)
    result = pd.concat([result_start, result_end], ignore_index=True)

    result["DateString"] = result_start.TARGETDATE.str.cat(result_end.TIME, sep=" ")
    result = result.dropna(subset=["DateString"])
    result["Date"] = result["DateString"].apply(build_date)
    result["ts"] = result["Date"].apply(utils.date_as_unix)
    deduped = result.drop_duplicates(subset=["Date"], keep="first")

    sorted_records = deduped.sort_values(by=["Date"])

    interp = pchip(sorted_records["ts"], sorted_records["FORECASTDEMAND"])
    return interp


def wind_format(date_string):
    return datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ").astimezone(datetime.timezone.utc)
    


def process_wind_forecast(res_list):
    result = pd.read_csv(
        res_list
    )
    try:
        result = result[["Datetime_GMT", "Incentive_forecast"]]
    except KeyError:
        result = result[["Datetime", "Wind_Forecast"]]
        result.columns = ["Datetime_GMT", "Incentive_forecast"]
    result["Date"] = result["Datetime_GMT"].apply(wind_format)
    result["ts"] = result["Date"].apply(utils.date_as_unix)
    result.drop(["Datetime_GMT"], axis=1)

    return result
