from airflow import DAG
from datetime import timedelta, datetime
from airflow.providers.http.sensors.http import HttpSensor
import json
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
import pandas as pd


def kelvin_to_fahrenheit(temp_in_kelvin):
    temp_in_fahrenheit = (temp_in_kelvin - 273.15) * (9/5) + 32
    return temp_in_fahrenheit


def transform_load_data(task_instance):
    data = task_instance.xcom_pull(task_ids="extract_weather_data")
    city = data["name"]
    weather_description = data["weather"][0]['description']
    temp_fahrenheit = kelvin_to_fahrenheit(data["main"]["temp"])
    feels_like_fahrenheit = kelvin_to_fahrenheit(data["main"]["feels_like"])
    min_temp_fahrenheit = kelvin_to_fahrenheit(data["main"]["temp_min"])
    max_temp_fahrenheit = kelvin_to_fahrenheit(data["main"]["temp_max"])
    pressure = data["main"]["pressure"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]
    time_of_record = datetime.utcfromtimestamp(data['dt'] + data['timezone'])
    sunrise_time = datetime.utcfromtimestamp(data['sys']['sunrise'] + data['timezone'])
    sunset_time = datetime.utcfromtimestamp(data['sys']['sunset'] + data['timezone'])

    transformed_data = {
        "City": city,
        "Description": weather_description,
        "Temperature (F)": temp_fahrenheit,
        "Feels Like (F)": feels_like_fahrenheit,
        "Minimum Temp (F)": min_temp_fahrenheit,
        "Maximum Temp (F)": max_temp_fahrenheit,
        "Pressure": pressure,
        "Humidity": humidity,
        "Wind Speed": wind_speed,
        "Time of Record": time_of_record,
        "Sunrise (Local Time)": sunrise_time,
        "Sunset (Local Time)": sunset_time
    }

    transformed_data_list = [transformed_data]
    df_data = pd.DataFrame(transformed_data_list)
    aws_credentials = {"key": "AKIA6GBMFMDLGSWPYZXZ", "secret": "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", "token": "FwoGZXIvYXdzEBIaDJDrUU10KhxOlaFL4CJqjOzV5Hqf9sypGCezCVM0/l9cZMfEfrYlNcaSTNGp77VwGJGczgO4Vxy0SifMNVBgKv2Xz+ojWeMs4gJpwB5bnNcvXg9GQdO/8dgYzHepexcCkZmQ0gh04ZYUwFHTZbfevYu61J1srnOE7Si+mK6zBjIoPScirN+2+WNCNYo8Sjt3yixlA1psZiNp0rAilNmAD6TJSnsiFCvUKQ=="}

    now = datetime.now()
    dt_string = now.strftime("%d%m%Y%H%M%S")
    dt_string = 'current_weather_data_portland_' + dt_string
    df_data.to_csv(f"s3://weatherapiairflowgayu/{dt_string}.csv", index=False, storage_options = aws_credentials)


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 6, 13),
    'email': ['gayathrikotha2001@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=2)
}

with DAG('weather_dag',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False) as dag:

    is_weather_api_ready = HttpSensor(
        task_id='is_weather_api_ready',
        http_conn_id='weathermaps_api',
        endpoint='/data/2.5/weather?q=Portland&APPID=3685d52cdf83209f379118327f70f1d3'
    )

    extract_weather_data = SimpleHttpOperator(
        task_id='extract_weather_data',
        http_conn_id='weathermaps_api',  # Make sure this matches with HttpSensor
        endpoint='/data/2.5/weather?q=Portland&APPID=3685d52cdf83209f379118327f70f1d3',
        method='GET',
        response_filter=lambda r: json.loads(r.text),
        log_response=True
    )

    transform_load_weather_data = PythonOperator(
        task_id='transform_load_weather_data',
        python_callable=transform_load_data
    )

    is_weather_api_ready >> extract_weather_data >> transform_load_weather_data
