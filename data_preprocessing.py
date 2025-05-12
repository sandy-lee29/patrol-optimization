import geopandas as gpd
import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import MinMaxScaler
import config


def load_shapefile():
    """Load the patrol sector shapefile and ensure 'Sector' is int."""
    beats = gpd.read_file(config.SHAPEFILE_PATH).to_crs(epsg=4326)
    beats["Sector"] = beats["Sector"].astype(int)
    return beats


def load_incident_data():
    """Load the incident CSV data."""
    df = pd.read_csv(config.YEAR_DATA_PATH)
    return df


def preprocess_incident_data(df):
    """Select relevant columns and clean the data."""
    selected_columns = ['Priority', 'lat', 'lon', 'Time Spent Responding', 'Dispositions']
    new_df = df[selected_columns].copy()
    return new_df


def replace_outliers_with_zero(df, column):
    """Replace outliers in a column with zero using IQR method."""
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    df[column] = df[column].apply(lambda x: config.OUTLIER_REPLACEMENT if x < lower_bound or x > upper_bound else x)
    return df


def extract_priority(level):
    if pd.isna(level) or str(level).strip() == "":
        return 0
    match = re.search(r'(\d+)', str(level))
    if match:
        priority = match.group(1)
        return 1 if priority == "1F" else int(priority)
    return 0


def get_disposition_weight(disposition):
    if pd.isna(disposition) or str(disposition).strip() == "":
        return 0.3
    disposition = str(disposition).lower()
    if "arrest" in disposition:
        return 1.0
    elif "case" in disposition:
        return 0.7
    else:
        return 0.3


def calculate_npps(df):
    """Calculate NPPS score for each row."""
    # Outlier handling
    df = replace_outliers_with_zero(df, 'Time Spent Responding')
    # Priority numeric
    df['Priority Numeric'] = df['Priority'].apply(extract_priority)
    # Priority weight
    df['Priority Weight'] = df['Priority Numeric'].apply(lambda x: config.PRIORITY_WEIGHTS.get(x, 0.0))
    # Scaled response time
    scaler = MinMaxScaler()
    df['Scaled Response Time'] = scaler.fit_transform(df[['Time Spent Responding']])
    # Disposition weight
    df['Disposition Weight'] = df['Dispositions'].apply(get_disposition_weight)
    # NPPS calculation
    w = config.NPPS_WEIGHTS
    df['NPPS'] = (
        w['priority'] * df['Priority Weight'] +
        w['response_time'] * df['Scaled Response Time'] +
        w['disposition'] * df['Disposition Weight']
    )
    return df 