## Project Overview

This project leverages Paris' Open Data by retrieving real-time data from Velib stations to optimize Lime's bike and scooter placement. We have created an infrastructure that ingests and visualizes this data in real-time, helping Lime to meet urban transport demands efficiently. The project encompasses data ingestion, ETL processes, predictive modeling, and user interface development.

## Problem Statements

In urban environments, efficiently managing the placement and availability of shared transportation resources such as bikes and scooters is crucial. 
Lime needs to optimize the deployment of its scooters to maximize their usage and meet demand effectively. 
This project addresses this by leveraging Paris' Open Data from Velib stations to predict bike availability. By implementing real-time data ingestion, processing, and predictive modeling, we aim to enhance the operational efficiency of Lime’s scooter placement and improve service availability, ensuring that scooters are strategically distributed based on current and anticipated demand.

## Data source

Velib Real-time Availability API: Provides current availability of bikes at Velib stations, updated every minute.
https://www.velib-metropole.fr/donnees-open-data-gbfs-du-service-velib-metropole 


## Project Architecture

The project architecture involves several components working together to collect, process, analyze, and visualize data. Below is a high-level overview:
- Data Ingestion: Real-time data ingestion from Velib API using Kafka Confluent during 4 days every hour.
- Data Storage: Storing ingested data in Amazon S3 bucket.
- ETL Process using Airflow to automated DAG:
    - Extract data from S3
    - Transform it using airflow
    - Load it into Amazon Redshift for data analysis
- Machine learning: Creating a predictive model to estimate bike availability at each station.
- API and User Interface: Serving the model using FastAPI and developing a user interface with Streamlit.
- Containerization: Using Docker and Docker Compose to manage and deploy the application.
      
<img width="1135" alt="Screenshot 2024-07-21 at 6 13 35 PM" src="https://github.com/user-attachments/assets/2f52aa23-903e-4f73-88bc-b403a9e666b4">


## Machine Learning
The data analysis phase involves:
Data Preparation: Cleaning and preparing the data for modeling.
Modeling: Creating a predictive model to estimate the number of bikes available at each station using machine learning techniques.
Model Evaluation: Evaluating model performance using appropriate metrics.

## API and User Interface
- FastAPI: Used to deploy the predictive model as an API. See below screenshots of the API.

<img width="1481" alt="Screenshot 2024-07-21 at 7 20 47 PM" src="https://github.com/user-attachments/assets/9823cec3-e3a3-46e3-bf39-87aab131d1b2">

<img width="1427" alt="Screenshot 2024-07-21 at 7 21 04 PM" src="https://github.com/user-attachments/assets/2fd0dbf6-2b11-46ce-8e95-a2cde3a9d335">

  
- Streamlit: Provides an interactive user interface to visualize predictions and filter stations based on bike availability. See below some screenshot of the app.
    - Green bicylcle: Velib' Station with zero availability.
    - Orange bicyle: Velib' Station with less than 10% availability.



<img width="717" alt="Screenshot 2024-07-21 at 5 42 31 PM" src="https://github.com/user-attachments/assets/1ae5768b-d601-45e8-977b-534fa50afeeb">
<img width="714" alt="Screenshot 2024-07-21 at 5 42 57 PM" src="https://github.com/user-attachments/assets/153bb70a-01c8-4a0c-afbd-913f8e4d163e">
<img width="720" alt="Screenshot 2024-07-21 at 5 43 10 PM" src="https://github.com/user-attachments/assets/386430f5-e0d0-407c-ab21-e2b3919403a8">

## Containerization
The project uses Docker and Docker Compose to ensure smooth deployment and communication between different components:
Docker: Creating images for each component (e.g., FastAPI, Streamlit).
Docker Compose: Managing multiple containers and enabling communication between them.

