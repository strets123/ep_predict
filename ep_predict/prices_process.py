import time

import dateutil
import pandas as pd

from ep_predict import utils


def process_agile_outgoing(csv_stringio):
    df = pd.read_csv(csv_stringio, usecols=[0, 4], names=["date", "price"], skiprows=1)
    df["Date"] = df["date"].apply(dateutil.parser.parse)
    df = df.drop(["date"], axis=1)
    last_date = df['Date'].iloc[-1] 
    next_date = last_date
    last_price = df['price'].iloc[-1] 
    while True:
        next_date = next_date + pd.Timedelta(30, "m")
        # Add 6 days of empty data to predict future prices
        if next_date >= (last_date + pd.Timedelta(1, "d")) and next_date.hour == 0:
            break
        df = df.append({"Date": next_date, "price": last_price}, ignore_index=True)    
    df["ts"] = df["Date"].apply(utils.date_as_unix)
    return df[["Date", "ts", "price"]]
