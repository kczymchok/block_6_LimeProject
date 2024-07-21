# Bike Availability Prediction for Lime using Velib Open Data

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
A. Data Ingestion: Real-time data ingestion from Velib API using Kafka Confluent during 4 days every hour.
B. Data Storage: Storing ingested data in Amazon S3.
C. ETL Process: Using Airflow for ETL to extract data from S3, transform it, and load it into Amazon Redshift.
D. Data Analysis and Modeling: Creating a predictive model to estimate bike availability at each station.
E. API and User Interface: Serving the model using FastAPI and developing a user interface with Streamlit.
F. Containerization: Using Docker and Docker Compose to manage and deploy the application.

Here is a simple flow chart:

```mermaid
graph TD;
    A -->B;
    A-->C;
    B-->D;
    C-->D;
```

```
+------------------------+   +--------------+   +-----+   +--------------+
|Random Forest Classifier+--->Stratification+--->SMOTE+--->RandomSearchCV|
+------------------------+   +--------------+   +-----+   +--------------+

```

## Technology and tools

- Kafka Confluent: For real-time data ingestion.
- Amazon S3: For data storage.
- Airflow: For ETL processes.
- Amazon Redshift: For data warehousing.
- FastAPI: For serving the predictive model.
- Streamlit: For developing the user interface.
- Docker & Docker Compose: For containerization and deployment.


## Data Ingestion and Storage

The data ingestion process involves:
Kafka Confluent: Used to retrieve real-time data from the Velib API.
Amazon S3: Data is stored in S3 for further processing.

## ETL Process
The ETL process using Airflow to automate the tasks includes:
Extract: Data is extracted from Amazon S3.
Transform: Data is cleaned and transformed into a suitable format for analysis.
Load: Transformed data is loaded into Amazon Redshift for analysis and machine learning.

## Data Analysis and Modeling
The data analysis phase involves:
Data Preparation: Cleaning and preparing the data for modeling.
Modeling: Creating a predictive model to estimate the number of bikes available at each station using machine learning techniques.
Model Evaluation: Evaluating model performance using appropriate metrics.

## API and User Interface
FastAPI: Used to deploy the predictive model as an API.
Streamlit: Provides an interactive user interface to visualize predictions and filter stations based on bike availability.
Containerization
The project uses Docker and Docker Compose to ensure smooth deployment and communication between different components:
Docker: Creating images for each component (e.g., FastAPI, Streamlit).
Docker Compose: Managing multiple containers and enabling communication between them.

