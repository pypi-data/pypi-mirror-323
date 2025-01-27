import requests
import pandas as pd
from typing import Dict

def vu_forecast_publish(
    api_key: str,
    group_name: str,
    series_name: str,
    raw_data: pd.DataFrame,
    forecast_data: pd.DataFrame,
    forecast_bounds: pd.DataFrame,
    forecast_residuals: pd.DataFrame,
    metadata: Dict[str, str],
    model_inputs: Dict[str, str],
    model_info: Dict[str, str],
):
    """
    Posts time series data, metadata to an API.

    Parameters:
        api_key (str): API key for authentication.
        group_name (str): The name of the group the series belongs to.
        series_name (str): The name of the series.
        raw_data (pd.DataFrame): DataFrame of raw time series data with columns ['date', 'value'].
        forecast_data (pd.DataFrame): DataFrame of forecast bounds with columns ['date', 'value'].
        forecast_bounds (pd.DataFrame): DataFrame of forecast data with columns ['date', 'lb95', ..., 'up95'].
        forecast_residuals (pd.DataFrame): DataFrame of forecast data with columns ['date', 'value'].
        metadata (Dict): Additional metadata characterizing the series and input parameters.
        model_info (Dict): Information about the forecasting model, including performance metrics.
        model_inputs (Dict): Information about the forecasting model, including performance metrics.

    Returns:
        Dict: Response from the API.
    """
    payload = {
        "groupName": group_name,
        "seriesName": series_name,
        "rawData": raw_data.to_dict(orient="records"),
        "forecastData": forecast_data.to_dict(orient="records"),
        "forecastBounds": forecast_bounds.to_dict(orient="records"),
        "forecastResiduals": forecast_residuals.to_dict(orient="records"),
        "metadata": metadata,
        "modelInfo": model_info,
        "modelInputs": model_inputs,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post("https://vu-forecast-ingestor.ricardofmteixeira.workers.dev", json=payload, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx, 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}