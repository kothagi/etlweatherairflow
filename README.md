# etlweatherairflow
## 🌟 ETL Weather Pipeline with Apache Airflow on AWS EC2 🌟
### Overview
#### This project demonstrates how to build and automate a Python ETL pipeline using Apache Airflow on AWS EC2. The pipeline extracts current weather data from the Open Weather Map API, transforms and loads the data into an AWS S3 bucket, and utilizes Apache Airflow for efficient workflow management and task scheduling.

## Project Highlights
##### Data Extraction: Fetches current weather data from the Open Weather Map API.
##### Data Transformation and Loading: Transforms and uploads the data to an AWS S3 bucket.
##### Workflow Management: Utilizes Apache Airflow for orchestrating and scheduling the ETL tasks.
## Key Learnings
##### Airflow DAGs and Operators: Created efficient workflows with Airflow.
##### AWS Integration: Deployed Airflow on EC2 and managed data in S3.
##### Automation: Developed reliable and automated data processing pipelines.
## Why It Matters
###### This project refined my skills in building scalable ETL pipelines and automating data workflows, crucial for effective data-driven decision-making.
```
Project Setup
Prerequisites
AWS Account
EC2 Instance
S3 Bucket
Python 3.6+
Apache Airflow
Installation
```
## Set up an EC2 instance:

##### Launch an EC2 instance on AWS.
##### SSH into your EC2 instance.
##### Install Apache Airflow:
```
sudo apt-get update
sudo apt-get install -y python3-pip
pip3 install apache-airflow
```

```export AIRFLOW_HOME=~/airflow
airflow db init
airflow users create --username admin --firstname FIRST_NAME --lastname LAST_NAME --role Admin --email admin@example.com
### Start the Airflow Web Server and Scheduler:
```
```
python
Copy code
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import requests
import json
import boto3

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'weather_etl',
    default_args=default_args,
    description='A simple ETL process for weather data',
    schedule_interval=timedelta(days=1),
)

def extract_weather_data():
    url = "http://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_API_KEY"
    response = requests.get(url)
    data = response.json()
    with open('/tmp/weather_data.json', 'w') as f:
        json.dump(data, f)

def upload_to_s3():
    s3 = boto3.client('s3')
    s3.upload_file('/tmp/weather_data.json', 'YOUR_S3_BUCKET_NAME', 'weather_data.json')

extract_task = PythonOperator(
    task_id='extract_weather_data',
    python_callable=extract_weather_data,
    dag=dag,
)

upload_task = PythonOperator(
    task_id='upload_to_s3',
    python_callable=upload_to_s3,
    dag=dag,
)

extract_task >> upload_task

```
#####  Usage
#####  Upload the weather_etl.py file to the dags folder in your Airflow directory.
#####  Access the Airflow Web UI at http://<your-ec2-public-dns>:8080 to monitor and manage the DAG.
##### Trigger the DAG manually or let it run on the defined schedule.
