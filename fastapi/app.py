from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
import math

# Initialize FastAPI app
app = FastAPI()

# Load the model
model_path = "/home/app/machine_learning/models/Gradient_Boosting_Regressor_best_model.joblib"
model = joblib.load(model_path)

# Define the request body structure
class BikePredictionRequest(BaseModel):
    year: int
    month: int
    day: int
    time_seconds: int
    stationcode: str
    capacity: float

@app.post("/predict")
def predict_bike_availability(request: BikePredictionRequest):
    features_dict = {
        "year": [request.year],
        "month": [request.month],
        "day": [request.day],
        "time_seconds": [request.time_seconds],
        "stationcode": [request.stationcode],
        "capacity": [request.capacity]
    }
    features_df = pd.DataFrame(features_dict)
    
    # Predict using the model
    try:
        prediction = model.predict(features_df)
        rounded_prediction = math.floor(prediction[0])
        return {"number_of_bikes": rounded_prediction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))