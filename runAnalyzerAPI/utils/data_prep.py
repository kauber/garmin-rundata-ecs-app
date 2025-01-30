import pandas as pd
from io import StringIO
from utils.utils_functions import hms_to_secs
from config import data_cols


def add_cols(data):
    """
    Add calculated fields to the DataFrame.

    Args:
        data (pd.DataFrame): The input dataset.

    Returns:
        pd.DataFrame: The updated dataset with additional fields.
    """
    # Ensure you're working with a copy of the DataFrame
    data = data.copy()

    # Convert 'Date' column to datetime and handle errors
    data['Date'] = pd.to_datetime(data['Date'], errors='coerce')

    # Ensure no invalid dates remain
    if data['Date'].isna().any():
        raise ValueError("Invalid or missing values in the 'Date' column.")

    # Create new columns
    data.loc[:, 'Short_date'] = data['Date'].dt.strftime('%Y-%m-%d')
    data.loc[:, 'Distance_in_miles'] = data['Distance'] / 1.609344
    data.loc[:, 'Time_in_secs'] = hms_to_secs(data['Time'])
    data.loc[:, 'Avg_pace_secs'] = hms_to_secs(data['Avg Pace'])
    data.loc[:, 'Best_pace_secs'] = hms_to_secs(data['Best Pace'])
    data.loc[:, 'Hour_of_day'] = data['Date'].dt.hour
    data.loc[:, 'Month'] = data['Date'].dt.month.astype(str)
    data.loc[:, 'Month_Year'] = data['Date'].dt.to_period('M')
    data.loc[:, 'Day_of_week'] = data['Date'].dt.dayofweek
    data.loc[:, 'Pace_MA_30'] = data['Avg_pace_secs'].rolling(30).mean()
    data.loc[:, 'Avg_HR_MA_30'] = data['Avg HR'].rolling(30).mean()
    data.loc[:, 'Year'] = data['Date'].dt.year

    return data


def fix_types(data):
    """
    fix data types
    :param data:
    :return:
    """
    data['Hour_of_day'] = data['Hour_of_day'].astype(str)
    data['Day_of_week'] = data['Day_of_week'].astype(str)
    data['Calories'] = data['Calories'].replace(',', '', regex=True).astype(int)
    data['Distance'] = data['Distance'].astype(float)
    return data


def load_data(file):
    """
    Load running activity data from a CSV file or file-like object.

    Args:
        file: Can be a file-like object (from UploadFile) or a file path (str).

    Returns:
        A Pandas DataFrame containing the loaded data.
    """
    try:
        if isinstance(file, str):  # If file is a path
            data = pd.read_csv(file)
            datap = data[data_cols]
            datap_out = add_cols(datap)
            datap_out = fix_types(datap_out)
        else:  # If file is a file-like object
            content = file.read().decode('utf-8')  # Decode byte content to string
            data = pd.read_csv(StringIO(content))  # Use StringIO to read as a DataFrame
            datap = data[data_cols]
            datap_out = add_cols(datap)
            datap_out = fix_types(datap_out)

        print(f"Loaded data with shape: {data.shape}")
        return datap_out
    except Exception as e:
        raise ValueError(f"Error loading file: {e}")
