# Electricity Price Prediction Demonstration

## Why?

Predicting electricity prices is useful if you are selling electricity to the grid. 
Day ahead prices are sometimes provided by suppliers but predicting 2 day ahead prices can be useful if you need longer lead times.

## How?

Reviewing the [literature reviews](https://reader.elsevier.com/reader/sd/pii/S0306261921004529?token=D118E0F0231D5E911794E540301B530DD09C16ED0755BC13FA6100B993CD0F904F86330471B8EE515952E1AF17A2A234&originRegion=eu-west-1&originCreation=20220928082105) we find that the Lasso Estimated AutoRegressive (LEAR) model is one of the best available.

## Which Data?

I have used a variety of datasets:

### National Grid ESO 

* [Forecast demand](https://data.nationalgrideso.com/demand/1-day-ahead-demand-forecast) (1 day ahead)
* [Forecast Demand](https://data.nationalgrideso.com/demand/7-day-ahead-national-forecast/r/7_day_ahead_demand_forecast) (7 days ahead)
* [Wind forecast](https://data.nationalgrideso.com/demand/day-ahead-wind-forecast/r/historic_day_ahead_wind_forecasts) (1 day ahead)
* [Wind Forecast](https://data.nationalgrideso.com/demand/14-days-ahead-wind-forecasts) (14 days ahead)

These datasets are correlated with the trend in electricity prices.

The price chosen is the price paid for export of solar energy in South East England (Available [here](https://www.energy-stats.uk/download-historical-pricing-data/))

### Results

