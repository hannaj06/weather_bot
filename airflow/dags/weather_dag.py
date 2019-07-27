from bs4 import BeautifulSoup
from pprint import pprint
from datetime import datetime
from airflow.operators.python_operator import PythonOperator
import requests
import configparser
import os
import airflow


def fetch_basin_image():
    SE_feed = 'http://sailing.mit.edu/img/SE/latest.jpg'
    r = requests.get(SE_feed)

    with open('basin_feed.jpg', 'wb') as fl:
        fl.write(r.content)


def gather_weather_data():
    mit_r = requests.get('http://sailing.mit.edu/weather')
    usga_r = requests.get('https://waterdata.usgs.gov/nwis/uv?site_no=01104500')

    usga_html = usga_r.text
    weather_html = mit_r.text

    mit_station = BeautifulSoup(weather_html, 'html.parser')
    usga_station = BeautifulSoup(usga_html, 'html.parser')

    weather_vars = {
    'temp': mit_station.find('a', class_='popup', href='dayouttemphilo.png').contents[0],
    'humidity': mit_station.find('a', class_='popup', href='dayouthum.png').contents[0],
    'wind': mit_station.find('a', class_='popup', href='daywind.png').contents[0],
    'wind_dir': mit_station.find('a', class_='popup', href='daywinddir.png').contents[0],
    'water_temp': mit_station.find('a', class_='popup', href='daywatertemphilo.png').contents[0],
    'flow': usga_station.find('td', class_='highlight2').contents[0],
    'ts': datetime.now().strftime('%m-%d-%Y  %X')
    }
    pprint(weather_vars)

    #gather creds
    config_file = os.path.join(os.environ['HOME'], '.databases.conf')
    creds = configparser.ConfigParser()
    creds.read(config_file)    
    bot_id = creds.get('groupme', 'weather_bot')
    access_token = creds.get('groupme', 'access_token')


    #post basin image
    with open('basin_feed.jpg', 'rb') as fl:
        image_req = requests.post(
            'https://image.groupme.com/pictures', 
            data=fl.read(),
            headers={'Content-Type': 'image/jpeg',
                    'X-Access-Token': access_token})

        image_url = image_req.json().get('payload').get('picture_url')


    speak = '''
Weather Bot 
{ts}
-----------------------
Temp: {temp} F
Humidity: {humidity}%
Wind: {wind} MPH {wind_dir}
Flow: {flow} ft^3/s
Water Temp: {water_temp} F
    '''.format(**weather_vars)

    print(speak)
    
    payload = {
    'bot_id': bot_id,
    'text': speak
    }

    url = 'https://api.groupme.com/v3/bots/post'
    r_text = requests.post(url, params=payload)
    pprint(r_text)

    if image_url is not None:    
        payload['text'] = image_url
        r_image = requests.poast(url, params=payload)
        pprint(r_image)

    

default_args = {
    'owner': 'joe',
    'start_date': airflow.utils.dates.days_ago(2)
}


dag = airflow.models.DAG(
    dag_id='weather_bot',
    schedule_interval='0 9 * * *',
    catchup=False,
    max_active_runs=1,
    default_args=default_args)


image_dl = PythonOperator(
    task_id='download_basin_image',
    python_callable=fetch_basin_image,
    dag=dag
    )

scrap_vars = PythonOperator(
    task_id='gather_weather_data',
    python_callable=gather_weather_data,
    dag=dag
    )


image_dl.set_downstream(scrap_vars)