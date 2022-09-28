import datetime
import json
import os
import shutil
import ep_predict
import pandas as pd

HTML = open("ep_predict/template.html").read()


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
    times = [{"Time": f"{str(n).zfill(2)}:00", "Predicted Price": df_record[f"h{n}"] } for n in range(24)]
    
    vega = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "description": "A simple bar chart with embedded data.",
        "title": f"Predicted Electricty Prices for {name} ({pd.to_datetime(str(df_record['Date'])).strftime('%b %d %Y')})",
        "data": {
            "values": times
        },
        "width": 600,
        "height": 300,
        "mark": "bar",
        "encoding": {
            "x": {"field": "Time", "type": "nominal", "axis": {"labelAngle": 90}},
            "y": {"field": "Predicted Price", "type": "quantitative"}
        }
    }
    return json.dumps(vega)


def main():
    df = fetch_data_and_make_prediction()
    prediction_date = datetime.datetime.now() 
    predictions = ep_predict.prices_predict.run(
        "octopus_agile_se_england", prediction_date
    )
    predictions = predictions.reset_index()
    records = predictions.to_records(index=False)
    tomorrow = output_json(records[0], "Today")
    day_after_tomorrow = output_json(records[1], "Tomorrow")
    html = HTML.format(tomorrow=tomorrow,day_after_tomorrow=day_after_tomorrow)
    print("---HTML---")
    print(html)
    print("---HTML---")
if __name__ == "__main__":
    main()
