import uvicorn
from fastapi import FastAPI, Request
import pandas as pd
from pydantic import BaseModel
from typing import Literal, List, Union
import joblib
from model_definition import SVR_with_InverseScaler 

import __main__
__main__.SVR_with_InverseScaler = SVR_with_InverseScaler 


# description will apear in the doc
description = """
Welcome to the Getaround API! 🚗 🚗\n
Getaround API is for helping you estimate the rental price of a vehicle per day. 
\n\n
Founded in 2009 with the goal to create a more affordable alternative to car-rental, 
Getaround has rapidly increased its market share and 
connected thousands of users in this car-sharing community.
\n\n
Trained on a dataset of 4,843 rentals, the goal of Getaround API is designed to serve information that could help
our users to achieve an indicative estimatation of daily rental revenue of their vehicles.
\n\n

The API has 3 groups of endpoints: \n

## Introduction Endpoints \n
- **/**: the greeting page that directs you to the API documentation \n
- **/preview**: a **GET** request that allows you to see random examples from data
\n
## Search and Filter Endpoints \n
- **/search_model/{model_key}** : a **GET** request to retrieve data for a car model you select \n
- **/search_type/{car_type}** : a **GET** request to retrieve data for a car type you select \n
- **/search_fuel/{fuel}** : a **GET** request to retrieve data for the fuel type you select \n
\n
## AI Solutions Endpoints
- **/predict**: returns the predicted price of a car based on the information you provide


"""

tags_metadata = [
    {
        "name": "Introduction Endpoints",
        "description": "Simple endpoints to try out!",
    },

    {
        "name": "Data Exploration Endpoints",
        "description": "More complex endpoints that deals with actual data with **GET** requests."
    },

    {
        "name": "AI Solutions Endpoints",
        "description": "Prediction Endpoint that deals with **POST** requests."
    }
]


app = FastAPI(
    title="Getaround API",
    description=description,
    version="0.1",
    contact={
        "name": "Hello, if you are interested in details of this project, check out my github.",
        "url": "https://github.com/yhaslan",
    },
    #openapi_tags=tags_metadata
)

@app.get("/", tags=["Introduction Endpoints"])
async def root():
    message = """Welcome to the Getaround API!🚗 \n
    To discover more on car-sharing and rental price optimization, check out documentation of the api at `/docs`."""
    return message

@app.get("/preview", tags=["Introduction Endpoints"])
async def print_samples():
    """
    display 10 random examples from the dataset

    """
    data = pd.read_csv("https://jedha-getaround-project.s3.amazonaws.com/pricing_data_cleaned.csv")
    sample = data.sample(10)

    return sample.to_dict()

@app.get("/Search_model/{model_key}", tags=["Data Exploration Endpoints"])
async def search_model(model_key: object):
    """
    Search data per model name : \n
    'Citroën', 'Peugeot', 'PGO', 'Renault', 'Audi', 'BMW', 'Ford',
    'Mercedes', 'Opel', 'Porsche', 'Volkswagen', 'KIA Motors',
    'Alfa Romeo', 'Ferrari', 'Fiat', 'Lamborghini', 'Maserati',
    'Honda', 'Mazda', 'Mitsubishi', 'Nissan', 'SEAT', 'Subaru',
    'Toyota', 'Suzuki', 'Yamaha'
   
    """
    model_list = ['Citroën', 'Peugeot', 'PGO', 'Renault', 'Audi', 'BMW', 'Ford',
    'Mercedes', 'Opel', 'Porsche', 'Volkswagen', 'KIA Motors',
    'Alfa Romeo', 'Ferrari', 'Fiat', 'Lamborghini', 'Maserati',
    'Honda', 'Mazda', 'Mitsubishi', 'Nissan', 'SEAT', 'Subaru',
    'Toyota', 'Suzuki', 'Yamaha']
    try:
        if model_key not in model_list:
            raise ValueError("You entered an input outside the allowed list of keys")
        data = pd.read_csv("https://jedha-getaround-project.s3.amazonaws.com/pricing_data_cleaned.csv")

        model = data[data["model_key"]==model_key]

        return model.to_dict()
    
    except Exception as e:
        return {"error": str(e)}


@app.get("/Search_type/{car_type}", tags=["Data Exploration Endpoints"])
async def search_type(car_type: object):
    """
    Search data for the selected type of car : \n
    'convertible', 'coupe', 'estate', 'hatchback', 'sedan',
    'subcompact', 'suv', 'van'
   
    """
    type_list = ['convertible', 'coupe', 'estate', 'hatchback', 'sedan',
    'subcompact', 'suv', 'van']

    try:
        if car_type not in type_list:
            raise ValueError("You entered an input outside the allowed list of car types")
        data = pd.read_csv("https://jedha-getaround-project.s3.amazonaws.com/pricing_data_cleaned.csv")

        cartype = data[data["car_type"]==car_type]

        return cartype.to_dict()
    
    except Exception as e:
        return {"error": str(e)}

@app.get("/Search_fuel/{fuel}", tags=["Data Exploration Endpoints"])
async def search_fuel(fuel: object):
    """
    Search data for the selected type of fuel : \n
    'diesel', 'petrol', 'hybrid_petrol', 'electro'
   
    """

    fuel_list = ['diesel', 'petrol', 'hybrid_petrol', 'electro']
    try:
        if fuel not in fuel_list:
            raise ValueError("You entered an input outside the allowed list of car types")
        data = pd.read_csv("https://jedha-getaround-project.s3.amazonaws.com/pricing_data_cleaned.csv")

        fuel = data[data["fuel"]==fuel]

        return fuel.to_dict()
    
    except Exception as e:
        return {"error": str(e)}


# Defining required input for the prediction endpoint
class Features(BaseModel):
    model_key: str
    mileage: Union[int, float]
    engine_power: Union[int, float]
    fuel: str
    paint_color: str
    car_type: str
    private_parking_available: bool
    has_gps: bool
    has_air_conditioning: bool
    automatic_car: bool
    has_getaround_connect: bool
    has_speed_regulator: bool
    winter_tires: bool



@app.post("/predict", tags=["AI Solutions Endpoints"])
async def predict(Features: Features):
    """
    Get the estimated rental price of for your car after providing the relevant information.\n
    Here is an example input: \n
  {\n
  "model_key": "Porsche",\n
  "mileage": 30000,\n
  "engine_power": 220,\n
  "fuel": "diesel",\n
  "paint_color": "black",\n
  "car_type": "sedan",\n
  "private_parking_available": True,\n
  "has_gps": False,\n
  "has_air_conditioning": True,\n
  "automatic_car": False,\n
  "has_getaround_connect": True,\n
  "has_speed_regulator": True,\n
  "winter_tires": True\n
  }
  \n
    The returned output is: {predictions: 187.07583181261413}

    """

    data = pd.DataFrame(dict(Features), index=[0])
    
    # Load the model & preprocessor
    try:
        model = joblib.load('svr_model.pkl')
        preprocessor = joblib.load('preprocessor.pkl')
    except Exception as e:
        return {"error": str(e)}  # Return error message if loading fails

    # Assuming the preprocessor is a StandardScaler or a similar transformer
    try:
        X = preprocessor.transform(data)
    except Exception as e:
        return {"error": str(e)}  # Return error message if transformation fails

    try:
        preds = model.predict(X)
        return {"prediction": round(preds[0],2)}
    except Exception as e:
        return {"error": str(e)}  # Return error message if prediction fails


if __name__ == "__main__":
    uvicorn.run(app, host = "0.0.0.0", port = 4000, debug=True, reload=True)



