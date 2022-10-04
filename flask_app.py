from flask import Flask, render_template, url_for
import requests
import urllib
import json
from requests.auth import AuthBase
from Crypto.Hash import HMAC
from Crypto.Hash import SHA256
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from pandas import json_normalize
import numpy as np
import pandas as pd
import math
from cla import publicKey, privateKey
app = Flask(__name__)


@app.route('/mapa', methods=["GET", "POST"])
def mapa():
    return render_template('mapa.html')

@app.route('/')
def home_page():
    # HMAC Authentication credentials

    # Class to perform HMAC encoding
    class AuthHmacMetosGet(AuthBase):
        # Creates HMAC authorization header for Metos REST service GET request.
        def __init__(self, apiRoute, publicKey, privateKey):
            self._publicKey = publicKey
            self._privateKey = privateKey
            self._method = 'GET'
            self._apiRoute = apiRoute

        def __call__(self, request):
            dateStamp = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
            print("timestamp: ", dateStamp)
            request.headers['Date'] = dateStamp
            msg = (self._method + self._apiRoute + dateStamp + self._publicKey).encode(encoding='utf-8')
            h = HMAC.new(self._privateKey.encode(encoding='utf-8'), msg, SHA256)
            signature = h.hexdigest()
            request.headers['Authorization'] = 'hmac ' + self._publicKey + ':' + signature
            return request

    # Endpoint of the API, version for example: v1
    apiURI = 'https://api.fieldclimate.com/v2'

    # Service/Route that you wish to call
    apiRoute = '/data/0020B01A/hourly/last/1h'
    apiRoute2 = '/data/0020B01A/hourly/last/48h'

    auth = AuthHmacMetosGet(apiRoute, publicKey, privateKey)
    response = requests.get(apiURI + apiRoute, headers={'Accept': 'application/json'}, auth=auth)

    auth2 = AuthHmacMetosGet(apiRoute2, publicKey, privateKey)
    response2 = requests.get(apiURI + apiRoute2, headers={'Accept': 'application/json'}, auth=auth2)

    df = json_normalize((response.json()['data']))
    df2 = json_normalize((response2.json()['data']))

    pd.set_option('display.max_columns', 150)
    #print(df)
    #print(df2)

    valoressum= df2['values.sum']
    valores2 = df2['values.avg']
    valoresmin = df2['values.min']
    valoresmax = df2['values.max']
    ppt=valoressum[3]

    pp= round((sum(ppt[24:48])),1)
    tmax= round(max(valoresmax[6][24:48]),1)
    tmin=round(min(valoresmin[6][24:48]),1)

    marchaviento = valores2[11]
    marchadirviento = valores2[12]
    marchatmed=valores2[6]
    marcharad = valores2[0]
    marchatsuelo = valores2[1]
    marchahum = valores2[7]
    marchapuntorocio = valores2[8]
    marchatmax=valoresmax[6]
    marchatmin=valoresmin[6]
    unidades = df['unit'].tolist()
    nombres = df['name'].tolist()
    valores = df['values.avg']

    wind= "Sensor no responde" if str(valores[11])=="nan" else str(valores[11][0])+ " km/h"


    radiacion =str(round(valores[0][0],1)) + " " + str(unidades[0])
    temp_suelo = str(round(valores[1][0],1)) + " " + str(unidades[1])
    temp_air =str(round(valores[6][0],1)) + " " + str(unidades[6])
    humedad = str(round(valores[7][0],1)) + " " + str(unidades[7])
    now= datetime.now()- timedelta(hours=3)
    hour= str(now.hour)
    hour1=str((datetime.now()- timedelta(hours=2)).hour)
    date = str(now.day) + "/" + str(now.month)
    hours=[47,46,45,44,43,42,41,40,39,38,37,36,35,34,33,32,31,30,29,28,27,26,25,24,23,22,21,20,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0]
    d=[]
    for i in hours:
        d.append(((datetime.now() - timedelta(hours=3 )- timedelta(hours=i)).hour))

    return render_template('ema.html',d=d,hour1=hour1,wind=wind,puntorocio=marchapuntorocio,mrad=marcharad,mhum=marchahum,mpp=ppt,mtsuelo=marchatsuelo,mtmed=marchatmed,tmax=tmax,tmin=tmin, rad=radiacion,pp=pp, temp= temp_suelo, temp2=temp_air, hum=humedad,hora=hour,date=date)





if __name__ == '__main__':
    app.run(debug=True)