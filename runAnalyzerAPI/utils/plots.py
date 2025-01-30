import numpy as np


def get_histogram_data(data, fields, bins=10):
    """
    Compute histogram data for the specified fields and return it in a UI-friendly format.

    Args:
        data (pd.DataFrame): Dataset containing the fields to histogram.
        fields (list): List of fields for which to generate histograms.
        bins (int): Number of bins for the histogram.

    Returns:
        dict: Dictionary containing histogram data (bins and counts) for each field.
    """
    try:
        histogram_data = {}

        for field in fields:
            if field in data.columns:
                # Compute histogram bins and counts
                counts, bin_edges = np.histogram(data[field], bins=bins)

                # Format bins as midpoints for clarity
                bin_midpoints = [(bin_edges[i] + bin_edges[i + 1]) / 2 for i in range(len(bin_edges) - 1)]

                # Store data in JSON-friendly format
                histogram_data[field] = {
                    "bins": bin_midpoints,
                    "counts": counts.tolist()
                }
            else:
                histogram_data[field] = {"error": f"{field} not found in dataset"}

        return histogram_data
    except Exception as e:
        raise ValueError(f"Error generating histogram data: {e}")


def get_mov_avg_data(data):
    """
    Prepare time series data for Average HR and Average Pace, including their moving averages.

    Args:
        data (pd.DataFrame): Dataset containing 'Date', 'Avg HR', 'Avg HR_MA_30',
                             'Avg_pace_secs', and 'Pace_MA_30'.

    Returns:
        dict: Dictionary containing time series data for HR and Avg Pace with moving averages.
    """
    try:
        # Check if required columns exist
        required_columns = ['Date', 'Avg HR', 'Avg_HR_MA_30', 'Avg_pace_secs', 'Pace_MA_30']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

        # Prepare time series data
        mov_avg_data = {
            "Avg HR": {
                "dates": data["Date"].astype(str).tolist(),
                "values": data["Avg HR"].tolist(),
                "moving_average": data["Avg_HR_MA_30"].tolist()
            },
            "Avg Pace": {
                "dates": data["Date"].astype(str).tolist(),
                "values": data["Avg_pace_secs"].tolist(),
                "moving_average": data["Pace_MA_30"].tolist()
            }
        }

        return mov_avg_data
    except Exception as e:
        raise ValueError(f"Error generating moving average data: {e}")


