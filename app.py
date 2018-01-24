import os
import requests
from flask import Flask, render_template, request
import json
import datetime
import time

#Predix service url
INGEST_URL = 'wss://gateway-predix-data-services.run.aws-usw02-pr.ice.predix.io/v1/stream/messages'
QUERY_URL='https://time-series-store-predix.run.aws-usw02-pr.ice.predix.io/v1/datapoints'

#UAA client id and password
data ={'grant_type':'client_credentials','client_id':'<your client id>','client_secret':'<your client secret','response_type':'token'}
uaa ='https://<your uaa serice id>.predix-uaa.run.aws-usw02-pr.ice.predix.io/oauth/token'

#Get access_token by http post
res = requests.post(uaa, data=data)
access_token =res.json()['access_token']
# time series service id
predix_zone_id = '<your time series service id>'
HEADERS = {'Predix-Zone-Id': predix_zone_id,\
           'Authorization': 'Bearer ' + access_token,\
           'Content-Type': 'application/json'}


def create_query_body(sensor_id, start_time, end_time):
    return {
        "cache_time": 0,
        "tags": [
            {
                "name": sensor_id,
                "order": "asc"
            }
        ],
        "start": start_time,
        "end": end_time
    }


def query_ts():
  # date about 10 min ago
  start_time = long(time.time()*1000 - 600000)
  end_time = long(time.time()*1000)
  query_body = json.dumps(create_query_body('MySensor', start_time, end_time))

  #query time series
  res = requests.post(QUERY_URL, data=query_body, headers=HEADERS)
  return res.json()['tags'][0]['results'][0]['values']


def gen_ui_data():
  ts_datas = query_ts()
  ts_msg = []
  for ts_data in ts_datas:
    ts_msg.append({"timeStamp": ts_data[0], "y0": ts_data[1]})
  ts_msg =  json.dumps(ts_msg)
  return ts_msg


#Python Flask framework
app = Flask(__name__)
port = int(os.getenv("PORT", 3000))

@app.route('/update')
def update():
    ts_msg = gen_ui_data()
    return ts_msg


@app.route('/')
def index():
  chart_data = {}
  return render_template('index.html', chart_data = chart_data)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=port)


