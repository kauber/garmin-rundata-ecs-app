from fastapi import APIRouter, UploadFile, HTTPException
from utils.data_prep import load_data
from utils.metrics import (
    get_descriptive_matrix,
    get_avg_pace_by_day_of_week,
    compute_totals,
    get_yearly_statistics,
    get_three_best_performances,
)
from utils.plots import get_histogram_data, get_mov_avg_data
from config import desc_matrix_cols, yearly_stats_cols, histogram_cols, main_distances
from utils.utils_functions import clean_nan_values
import os

# Debugging confirmation
print("Executing routes.py for /api/upload")

# Create the APIRouter instance
router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile):
    """
    Handle file upload and process the uploaded CSV file.
    """
    try:
        # Validate file type
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Only .csv files are supported")

        # breakpoint()

        # Save the uploaded file temporarily
        temp_file_path = f"temp/{file.filename}"
        with open(temp_file_path, "wb") as f:
            f.write(await file.read())

        # Debugging: Confirm file was saved
        # print(f"Uploaded file saved at: {temp_file_path}")

        # Load and process the CSV file
        data = load_data(temp_file_path)

        # Validate and debug dataset structure
        # print(f"Dataset columns: {data.columns}")
        # print(f"Dataset preview:\n{data.head()}")

        # Metrics
        desc_matrix = get_descriptive_matrix(data, desc_matrix_cols)
        avg_pace_day_week = get_avg_pace_by_day_of_week(data)
        totals = compute_totals(data)
        yearly_statistics = get_yearly_statistics(data, yearly_stats_cols)
        best_perf = get_three_best_performances(data, main_distances)

        # Histograms for Distance, Avg HR, Avg Pace
        histogram_data = get_histogram_data(data, histogram_cols, bins=10)

        # Time series data for Avg_pace_secs and Avg HR
        time_series_data = get_mov_avg_data(data)

        # Clean up the temporary file
        os.remove(temp_file_path)

        # Clean NaN values in all outputs
        desc_matrix = clean_nan_values(desc_matrix)
        avg_pace_day_week = clean_nan_values(avg_pace_day_week)
        totals = clean_nan_values(totals)
        yearly_statistics = clean_nan_values(yearly_statistics)
        histogram_data = clean_nan_values(histogram_data)
        time_series_data = clean_nan_values(time_series_data)
        best_perf = clean_nan_values(best_perf)

        # print("Debug: desc_matrix", desc_matrix)
        # print("Debug: avg_pace_day_week", avg_pace_day_week)
        # print("Debug: totals", totals)
        # print("Debug: yearly_statistics", yearly_statistics)
        # print("Debug: histogram_data", histogram_data)
        # print("Debug: time_series_data", time_series_data)
        # print("Debug: best_perf", best_perf)

        return {
            "desc_matrix": desc_matrix,
            "avg_pace_day_week": avg_pace_day_week,
            "totals": totals,
            "yearly_statistics": yearly_statistics,
            "histogram_data": histogram_data,
            "time_series_data": time_series_data,
            "best_perf": best_perf,
        }
    except HTTPException:
        raise  # Re-raise HTTP errors for expected cases
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Unexpected error: {str(e)}")
