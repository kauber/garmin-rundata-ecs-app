from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routes import router

# Initialize FastAPI app
app = FastAPI(
    title="Running Data Analysis API",
    description="API for analyzing running activity data, including metrics, histograms, and time series visualizations.",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://run-analyze-web-ui.s3-website.eu-central-1.amazonaws.com"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include routes from the api.routes module
app.include_router(router, prefix="/api")


@app.get("/")
def root():
    """
    Root endpoint to confirm the API is running.
    """
    return {"message": "Welcome to the Running Data Analysis API"}


# Explicitly handle OPTIONS preflight requests
@app.options("/{full_path:path}")
async def preflight_handler(full_path: str, request: Request):
    response = JSONResponse(content={"message": "Preflight request handled"})
    response.headers["Access-Control-Allow-Origin"] = "http://run-analyze-web-ui.s3-website.eu-central-1.amazonaws.com"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response
