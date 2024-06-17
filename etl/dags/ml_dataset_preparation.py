
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.models import Variable
import os
import json
import pandas as pd
from airflow.providers.amazon.aws.operators.redshift_data import RedshiftDataOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 3, 14),  # Adjust start date
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    's3_to_ml_to_AmazoneRedshiftServerless',
    default_args=default_args,
    description='Extract, transform, and load data from S3 to PostgreSQL',
    schedule_interval='@daily',  # Adjust as needed
    catchup=False,  # Set to False if you don't want historical backfill
)

def extract_data_from_s3():
    # Define your S3 bucket and key
    s3_bucket = 'velib-project'
    s3_prefix = 'realtime_data_velib/'  # Adjust as needed to match your file structure

    # Define local directory where files will be downloaded
    local_dir = '/opt/airflow/data/extracted_s3_data'
    os.makedirs(local_dir, exist_ok=True)

    # Initialize S3Hook
    s3_hook = S3Hook(aws_conn_id='aws_default')

    # List objects in S3 bucket
    s3_objects = s3_hook.list_keys(bucket_name=s3_bucket, prefix=s3_prefix)

    # Download files from S3 to local directory
    for s3_object in s3_objects:
        local_file_path = os.path.join(local_dir, os.path.basename(s3_object))
        with open(local_file_path, 'wb') as file:
            file.write(s3_hook.read_key(s3_object, s3_bucket).encode())
    
    # Log the files downloaded
    print(f"Downloaded {len(s3_objects)} file(s) from S3 to {local_dir}")


def transform_data():
    local_dir='/opt/airflow/data/extracted_s3_data'
    transformed_data_dir = '/opt/airflow/data/transformed_data'

    if not os.path.exists(transformed_data_dir):
        os.makedirs(transformed_data_dir)
    
    all_data=[]

    for filename in os.listdir(local_dir):
        if filename.endswith('.json'):
            with open(os.path.join(local_dir, filename),'r') as file:
                data = json.load(file)
                all_data.extend(data)
    
    df=pd.DataFrame(all_data)

    def extract_coordinates(coord_dict):
        if pd.isna(coord_dict):
            return None, None
        lon = coord_dict.get('lon')
        lat = coord_dict.get('lat')
        return lon, lat

    # Apply the function to extract longitude and latitude
    df['longitude'], df['latitude'] = zip(*df['coordonnees_geo'].apply(extract_coordinates))

# Convert numeric columns to numeric types, handle non-numeric values like '.'
    numeric_columns = ['capacity', 'numdocksavailable', 'numbikesavailable', 'mechanical', 'ebike']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

    column_types = {
        'stationcode': 'string',
        'name': 'string',
        'is_installed': 'bool',
        'is_renting': 'bool',
        'is_returning': 'bool',
        'nom_arrondissement_communes': 'string',
        'longitude': 'float64',
        'latitude': 'float64'
    }
    df = df.astype(column_types)

    #arrange the duedate columns for better analysis and data manipulation
    df['duedate']=pd.to_datetime(df['duedate'])

    df['date']=df["duedate"].dt.date
    df['year']=df['duedate'].dt.year
    df['month']=df['duedate'].dt.month
    df['day']=df['duedate'].dt.day
    df['time']=df['duedate'].dt.time

    # df['time'] = pd.to_datetime(df['time'], format='%H:%M:%S')
    # df['date']=pd.to_datetime(df['date'])


    # Drop the original 'coordonnees_geo' and duedate
    df = df.drop(columns=['coordonnees_geo', 'duedate'])

    transformed_file_path = os.path.join(transformed_data_dir, 'transformed_data.csv')
    df.to_csv(transformed_file_path, index=False)


    print(f"Transformed data saved to {transformed_file_path}")


def upload_to_s3(ti):
    """Uploads the transformed CSV file to S3 using hooks."""
    transformed_file_path = '/opt/airflow/data/transformed_data/transformed_data.csv'
    s3_key = 'transformed_data.csv'
    s3_bucket = 'velib-project'

    s3_hook = S3Hook(aws_conn_id="aws_default")
    s3_hook.load_file(
        filename=transformed_file_path,
        key=s3_key,
        bucket_name=s3_bucket,
        replace=True 
    )

setup__task_create_table2 = RedshiftDataOperator(
    task_id='setup_create_table', region='us-east-1', workgroup_name='redshift-velib',
    database='dev',
    sql="""
    DROP TABLE IF EXISTS transformed_data;
    CREATE TABLE transformed_data (
        stationcode VARCHAR(255),
        name VARCHAR(255),
        is_installed BOOLEAN,
        capacity INT,
        numdocksavailable INT,
        numbikesavailable INT,
        mechanical INT,
        ebike INT,
        is_renting BOOLEAN,
        is_returning BOOLEAN,
        nom_arrondissement_communes VARCHAR(255),
        code_insee_commune VARCHAR(255),
        longitude DOUBLE PRECISION, 
        latitude DOUBLE PRECISION, 
        date DATE, 
        year INT, 
        month INT, 
        day INT, 
        time TIME
    );
    """
)

# transfer_s3_to_redshift = RedshiftDataOperator(
#     task_id='load_data',
#     region='us-east-1', 
#     cluster_identifier='redshift-velib',
#     database='dev',
#     aws_conn_id='aws_default',
#     sql="""
#     COPY transformed_data
#     FROM 's3://velib-project/transformed_data.csv'
#     IAM_ROLE 'arn:aws:iam::891377001948:role/RedshiftCopyRoles'
#     FORMAT AS CSV
#     IGNOREHEADER 1;
#     """,
#     dag=dag,
# )

# transfer_s3_to_redshift = S3ToRedshiftOperator(
#     task_id="transfer_s3_to_redshift",
#     redshift_conn_id="redshift_conn_id",
#     s3_bucket="velib-project",
#     s3_key="transformed_data.csv",  # Replace with your actual S3 key
#     schema="public",
#     table="transformed_data",
#     copy_options=["csv"],
#     dag=dag,
# )

# transfer_s3_to_redshift = S3ToRedshiftOperator(
#     task_id="s3_to_redshift",
#     schema="PUBLIC",
#     table="transformed_data",
#     s3_bucket="velib-project",
#     s3_key="transformed_data.csv",
#     redshift_conn_id="redshift_conn_id",
#     aws_conn_id="aws_default",
#     sql="""
#     COPY transformed_data
#     FROM 's3://velib-project/transformed_data.csv'
#     IAM_ROLE 'arn:aws:iam::891377001948:role/RedshiftCopyRoles'
#     FORMAT AS CSV
#     IGNOREHEADER 1;
#     """,
#     dag=dag,  
# )

transfer_s3_to_redshift = S3ToRedshiftOperator(
    task_id="s3_to_redshift",
    schema="PUBLIC",
    table="transformed_data",
    s3_bucket="velib-project",
    s3_key="transformed_data.csv",
    copy_options=["csv", "IGNOREHEADER 1", "MAXERROR 1000","DELIMITER ','", "FILLRECORD"],  # Specify COPY options here
    aws_conn_id="aws_default",
    redshift_conn_id="redshift_conn_id",
    dag=dag,
)



extract_data_task = PythonOperator(
    task_id='extract_data_from_s3',
    python_callable=extract_data_from_s3,
    dag=dag,
)


transform_data_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=dag,
)

upload_to_bucket = PythonOperator(
    task_id= 'upload_to_s3',
    python_callable=upload_to_s3,
    dag=dag

)

extract_data_task >> transform_data_task >> upload_to_bucket >> setup__task_create_table2 >> transfer_s3_to_redshift



