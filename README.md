# JEDHA_Bloc5

This repository contains my deployment project for the validation of Bloc 5 of the RNCP certificate. 
Here is the description of the project:

- 1. Project Description
- 2. Deliverables
- 3. Organization of GitHub Repository
- 4. Links to the Heroku apps


## 1. Project Description: GetAround 

[GetAround](https://www.getaround.com/?wpsrc=Google+Organic+Search) is the Airbnb for cars. You can rent cars from any person for a few hours to a few days! Founded in 2009, this company has known rapid growth. In 2019, they count over 5 million users and about 20K available cars worldwide. 

As Jedha's partner, they offered this great challenges: 

### Context 

When renting a car, our users have to complete a checkin flow at the beginning of the rental and a checkout flow at the end of the rental in order to:

* Assess the state of the car and notify other parties of pre-existing damages or damages that occurred during the rental.
* Compare fuel levels.
* Measure how many kilometers were driven.

The checkin and checkout of our rentals can be done with three distinct flows:
* **📱 Mobile** rental agreement on native apps: driver and owner meet and both sign the rental agreement on the owner’s smartphone
* **Connect:** the driver doesn’t meet the owner and opens the car with his smartphone
* **📝 Paper** contract (negligible)

### Project 🚧

For this case study, we suggest that you put yourselves in our shoes, and run an analysis we made back in 2017 🔮 🪄

When using Getaround, drivers book cars for a specific time period, from an hour to a few days long. They are supposed to bring back the car on time, but it happens from time to time that drivers are late for the checkout.

Late returns at checkout can generate high friction for the next driver if the car was supposed to be rented again on the same day : Customer service often reports users unsatisfied because they had to wait for the car to come back from the previous rental or users that even had to cancel their rental because the car wasn’t returned on time.

### Goals 🎯

In order to mitigate those issues we’ve decided to implement a minimum delay between two rentals. A car won’t be displayed in the search results if the requested checkin or checkout times are too close from an already booked rental.
It solves the late checkout issue but also potentially hurts Getaround/owners revenues: we need to find the right trade off.

**Our Product Manager still needs to decide:**
* **threshold:** how long should the minimum delay be?
* **scope:** should we enable the feature for all cars?, only Connect cars?


## 2- Deliverables 📬

To complete this project, you should deliver:

- A **dashboard** in production (accessible via a web page for example). You can use `streamlit` or any other technology that you see fit. 
- The **whole code** stored in a **Github repository**. You will include the repository's URL.
- An **documented online API** on Heroku server (or any other provider you choose) containing at least **one `/predict` endpoint** that respects the technical description above. We should be able to request the API endpoint `/predict` using `curl`:

```shell
$ curl -i -H "Content-Type: application/json" -X POST -d '{"input": [[7.0, 0.27, 0.36, 20.7, 0.045, 45.0, 170.0, 1.001, 3.0, 0.45, 8.8]]}' http://your-url/predict
```

Or Python:

```python
import requests

response = requests.post("https://your-url/predict", json={
    "input": [[7.0, 0.27, 0.36, 20.7, 0.045, 45.0, 170.0, 1.001, 3.0, 0.45, 8.8]]
})
print(response.json())
```


## 3. Structure of this GitHub Repository
In this project repository you will find :
- a _README.md_ file where you will file the project description
- a _data_ folder in which you will find datasets get_around_dalay_analysis.xlsx and get_around_pricing_project.csv files
- a _notebooks_ folder in which you will find python notebooks for delay analysis project (GetAroundAnalysis_EDA.ipynb) and price estimation project(GetAroundAnalysis_EDA.ipynb). You can find more detailed analyses and visualizarions in these notebooks. The latter also contains an example python request to retrieve data from the API in the end.
- a _web-dashboard_ folder in which you will find:
    - a _Dockerfile_
    - a _requirements.txt_ file for the necessary packages
    - a folder named _.streamlit_ that contains the _config.toml_ file with my custom theme
    - an _app.py_ script for the streamlit dashboard
    - a _swarmplot.png_ file for one of the graphs in the dashboard that was inserted as an image since I liked better the seaborn version
- an _api_ folder in which you fill find:
    - a _Dockerfile_
    - a _requirements.txt_ file for the necessary packages
    - an _app.py_ script for the FAST API
    - pickle files for the trained model and preprocessor : svr_model.pkl and preprocessor.pkl
    - a model_definition.py script since I did not use the custom SVR model ok scikit-learn but instead generated a new class that allowed me to scale and unscale back the target variable y.
    
    

## 4. Links to Heroku apps:
Find below the applications as deployed on a Heroku Servr:
- Click [here](https://getaround-dahsboard-9e68fd3a473e.herokuapp.com/) for the webpage of the streamlit dashboard 
- Click [here](https://getraound-api-7d58c833a433.herokuapp.com/) for the documented online API on Heroku server 