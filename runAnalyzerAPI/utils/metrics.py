import pandas as pd
from utils.utils_functions import secs_to_hms


def get_descriptive_matrix(data, desc_matrix_cols):
    """
    Generate descriptive statistics and prepare for web display.

    Args:
        data (pd.DataFrame): Input dataset.

    Returns:
        dict: JSON-ready dictionary containing the descriptive statistics.
        :param data:
        :param desc_matrix_cols:
    """

    try:
        # Generate descriptive statistics
        stats = data[desc_matrix_cols].describe().transpose()

        # Add average pace row (converted to HH:MM:SS.ss format)
        if "Avg_pace_secs" in data.columns:
            avg_pace = data["Avg_pace_secs"].mean()  # Compute mean pace in seconds
            formatted_avg_pace = secs_to_hms(avg_pace)  # Convert to HH:MM:SS.ss
            stats.loc["Average Pace (HH:MM:SS.ss)"] = [""] * (stats.shape[1])  # Create an empty row
            stats.at["Average Pace (HH:MM:SS.ss)", "mean"] = formatted_avg_pace  # Add formatted pace to the row

        # Convert DataFrame to JSON-friendly format
        result = stats.reset_index().to_dict(orient="list")
        return result
    except Exception as e:
        raise ValueError(f"Error generating descriptive stats: {e}")


def get_avg_pace_by_day_of_week(data):
    """
    Compute the average pace per day of the week and format results.

    Args:
        data (pd.DataFrame): Input dataset containing 'Day_of_week' and 'Avg_pace_secs'.

    Returns:
        dict: Dictionary with days of the week as keys and formatted average paces as values.
    """
    try:
        # Mapping day numbers to day names
        day_mapping = {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday",
        }

        # Ensure valid data: Drop NaN values in Day_of_week and Avg_pace_secs
        valid_data = data.dropna(subset=["Day_of_week", "Avg_pace_secs"])

        # Ensure Day_of_week is an integer
        valid_data["Day_of_week"] = valid_data["Day_of_week"].astype(int)

        # Group by day of the week and compute the mean average pace in seconds
        avg_pace_by_day = valid_data.groupby("Day_of_week")["Avg_pace_secs"].mean()

        # Convert day numbers to day names and format paces
        formatted_paces = {
            day_mapping[day]: secs_to_hms(pace) for day, pace in avg_pace_by_day.items()
        }

        return formatted_paces

    except KeyError as e:
        print(f"KeyError occurred: {e}")
        raise ValueError(f"Unexpected day of the week value: {e}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise


def compute_totals(data):
    """
    Compute total calories burnt and total distance run.

    Args:
        data (pd.DataFrame): Input dataset.

    Returns:
        dict: Total calories and total distance ready for UI display.
    """
    try:
        total_calories = data['Calories'].sum()
        total_distance = round(data['Distance'].sum(), 1)

        # Return totals in a dictionary format
        return {
            "total_calories": int(total_calories),  # Ensure calories is an integer
            "total_distance": total_distance  # Distance rounded to 1 decimal
        }
    except KeyError as e:
        raise ValueError(f"Missing column in dataset: {e}")
    except Exception as e:
        raise ValueError(f"Error computing totals: {e}")


def get_yearly_statistics(data, yearly_statistics_cols):
    """
    Compute year-on-year statistics (mean, std, min, max) for specified fields.

    Args:
        data (pd.DataFrame): Input dataset containing 'Year' and the specified fields.

    Returns:
        dict: Yearly statistics formatted for UI display.
        :param data:
        :param yearly_statistics_cols:
    """

    try:
        # Dictionary to hold results for all fields
        yearly_stats = {}

        for col in yearly_statistics_cols:
            if col in data.columns:
                # Group by 'Year' and calculate statistics
                stats = data.groupby('Year')[col].agg(['mean', 'std', 'min', 'max'])

                # Convert to a dictionary format for the UI
                yearly_stats[col] = stats.reset_index().to_dict(orient="list")
            else:
                yearly_stats[col] = {"error": f"{col} not found in dataset"}

        return yearly_stats
    except Exception as e:
        raise ValueError(f"Error computing yearly statistics: {e}")


def get_three_best_performances(data: pd.DataFrame, distances: list):
    """
    Function to compute the best performances based on main distances and return them in a format suitable for the UI.

    Args:
        data (pd.DataFrame): Dataset containing run information.
        distances (list): List of distances to evaluate.

    Returns:
        dict: Dictionary with distances as keys and top performances as values.
    """
    try:
        best_performances = {}

        for distance in distances:
            # Filter runs near the target distance
            filtered_runs = data[
                (data['Distance'] <= distance + 0.02) &
                (data['Distance'] >= distance - 0.02)
                ]

            # Get top performances sorted by average pace
            top_runs = (
                filtered_runs
                .sort_values(by=['Avg_pace_secs'])
                .head(3)
                [['Date', 'Distance', 'Time', 'Avg Pace']]
            )

            # Convert results to a JSON-friendly format
            best_performances[distance] = top_runs.to_dict(orient='records')

        return best_performances
    except Exception as e:
        raise ValueError(f"Error computing best performances: {e}")
