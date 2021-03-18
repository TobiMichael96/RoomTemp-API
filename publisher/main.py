#!/usr/bin/python
import logging
import os
import time

import Adafruit_DHT
import requests

sleep = 60
endpoint = os.getenv('URL')
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)

while True:
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 2)
    if humidity is not None and temperature is not None:
        logging.info("Temp: " + str(round(temperature, 3)) + " Humidity: " + str(round(humidity, 3)))
        answer = requests.post(endpoint, auth=(username, password),
                               json={"temperature": round(temperature, 3), "humidity": round(humidity, 3)})
        logging.info(answer.status_code)
        if answer.status_code != 201:
            logging.warning(answer.content)
    else:
        logging.error("This did not work, will try again...")
        sleep = 5
    time.sleep(sleep * 10)
    sleep = 60
