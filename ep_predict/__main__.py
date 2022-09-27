import datetime
import json
import os
import shutil
import ep_predict
import pandas as pd

def from_unixtime(unixtime):
    return datetime.datetime.fromtimestamp(unixtime).strftime("%Y-%m-%d %H:%M:%S")

def fetch_train_and_test_dataset():
    wind_forecast_list, future_wind = ep_predict.forecasts_fetch.fetch_wind_forecast()
    wind_forecast_df = ep_predict.forecasts_process.process_wind_forecast(
        wind_forecast_list
    )
    future_wind_df = ep_predict.forecasts_process.process_wind_forecast(
        future_wind
    )
    combined = pd.concat([wind_forecast_df, future_wind_df])
    combined.drop_duplicates(keep="first")
    demad_response, future_demand_response = ep_predict.forecasts_fetch.fetch_demand_forecast()
    demand_forecast_interpolator = ep_predict.forecasts_process.build_demand_forecast_interpolator(
        demad_response, future_demand_response
    )
    
    agile_outgoing_buffer = ep_predict.prices_fetch.fetch_agile_outgoing()
    agile_outgoing_se_england = ep_predict.prices_process.process_agile_outgoing(agile_outgoing_buffer)

    agile_outgoing_se_england["Demand_Forecast"] = agile_outgoing_se_england["ts"].apply(
        demand_forecast_interpolator
    )
    merged = pd.merge(left=agile_outgoing_se_england, right=combined, how="left", on="Date")
    output = merged.fillna(method='ffill')
    output = output.drop_duplicates(subset=["Date"])
    return output[["Date", "price", "Demand_Forecast", "Incentive_forecast"]].dropna().sort_values(by=["Date"])


def fetch_data_and_make_prediction():
    forecasts_and_prices = fetch_train_and_test_dataset()

    only_hourly_results = forecasts_and_prices[forecasts_and_prices["Date"].dt.minute == 0]
    only_2020_onwards = only_hourly_results[only_hourly_results["Date"].dt.year >=2020]

    try: 
        if os.path.exists("datasets") and os.path.isdir("datasets"):
            shutil.rmtree("datasets")
        os.mkdir("datasets")
    except OSError:
        pass
    only_2020_onwards.fillna(0).to_csv("datasets/octopus_agile_se_england.csv", index=False, date_format='%Y-%m-%d %H:%M:%S')
    return only_2020_onwards


def output_json(df_record, name):
    times = [f"{str(n).zfill(2)}:00" for n in range(24)]
    output = {"date": df_record["Date"], "values": [df_record[f"h{n}"] for n in range(24)], "labels": times}
    with open(f"website/{name}.json", "w") as f:
        json.dump(output)


def main():
    df = fetch_data_and_make_prediction()
    prediction_date = datetime.datetime.now() + datetime.timedelta(days=1)
    predictions = ep_predict.prices_predict.run(
        "octopus_agile_se_england", prediction_date
    )

    output_json(predictions[0], "hours_list_tomorrow")
    output_json(predictions[1], "day_after_tomorrow")

if __name__ == "__main__":
    main()
