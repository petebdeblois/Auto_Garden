import requests
import re
import time
from bs4 import BeautifulSoup
import influxdb_client
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# Influx
token = ''
org = ""
url = ""
client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
bucket = "dump"
write_api = client.write_api(write_options=SYNCHRONOUS)


# Weather
url = "https://xn--qubec-csa.weatherstats.ca/data/precipitation-daily.json"
querystring = {"refresh_count": "1", "browser_zone": "Eastern Daylight Time"}
payload = ""
headers = {
    "authority": "xn--qubec-csa.weatherstats.ca",
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9,fr;q=0.8",
    "cache-control": "no-cache",
    "dnt": "1",
    "pragma": "no-cache",
    "referer": "https://xn--qubec-csa.weatherstats.ca/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}


def get_rain():
  try:
    response = requests.request(
        "GET", url, data=payload, headers=headers, params=querystring)
    resultJSON = response.json()
    rain_yesterday = resultJSON['rows'][0]['c'][1]['v']
    data = {"state": rain_yesterday}
    return float(rain_yesterday)
  except Exception as e:
      print(f'{e}')


def send_rain_to_influx(rain):
  point = (
      Point("rain")
      .field("precipitation", rain)

  )
  print(point)
  write_api.write(bucket=bucket, org="uat", record=point)
  time.sleep(1)  # separate points by 1 second


if __name__ == "__main__":
  rain_yesterday = get_rain()
  send_rain_to_influx(rain_yesterday)
