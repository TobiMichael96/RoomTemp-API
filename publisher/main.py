#!/usr/bin/python
import sys
import Adafruit_DHT
import requests
import time
import os


sleep = 60

while True:
	humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 2)
	if humidity is not None and temperature is not None:
		print("Temp: " + str(round(temperature, 3)) + " Humidity: " + str(round(humidity, 3)))
		answer = requests.put(os.getenv('URL'), auth=(os.getenv('USERNAME'), os.getenv('PASSWORD')), json={"temperature": round(temperature, 3), "humidity": round(humidity, 3)})
		print(answer)
		sleep = 5
	time.sleep(sleep)
	sleep = 60
