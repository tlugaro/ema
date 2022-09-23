from flask import Flask, render_template, url_for
from flask_wtf import FlaskForm
from flask import send_file
import folium
from folium import plugins
import urllib
import json
from urllib import request
import requests
from requests.auth import AuthBase
from Crypto.Hash import HMAC
from Crypto.Hash import SHA256
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from pandas import json_normalize
import pandas as pd
from osgeo import gdal
from osgeo import ogr
import numpy as np
import pandas as pd
import geopandas
import psycopg2
import math

app = Flask(__name__)


@app.route('/mapa', methods=["GET", "POST"])
def mapa():
    return render_template('mapa.html')

@app.route('/')
def home_page():
    # HMAC Authentication credentials
    publicKey = 'cbbc417983f46ad4292a4ea93f6b4dff7074c20d7bc1b7e0'
    privateKey = 'e2c745bf445a99390999bcce7d7e424beef75b7e2234db78'

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
    apiRoute2 = '/data/0020B01A/hourly/last/24h'

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

    pp= round((sum(ppt)),2)
    tmax= max(valoresmax[6])
    tmin=min(valoresmin[6])

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

    wind=  str(valores[11][0])
    winddir = str(valores[12])
    eto = str(valores[22]) + " " + str(unidades[22])
    radiacion =str(valores[0][0]) + " " + str(unidades[0])
    temp_suelo = str(valores[1][0]) + " " + str(unidades[1])
    temp_air =str(valores[6][0]) + " " + str(unidades[6])
    humedad = str(valores[7][0]) + " " + str(unidades[7])
    now= datetime.now()
    hour= str(now.hour)+":"+str(now.minute)
    date = str(now.day) + "/" + str(now.month)
    hours=[23,22,21,20,19,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0]
    d=[]
    for i in hours:
        d.append(((datetime.now() - timedelta(hours=i)).hour))

    return render_template('ema.html',d=d,windir=winddir,wind=wind,puntorocio=marchapuntorocio,eto=eto,mrad=marcharad,mhum=marchahum,mpp=ppt,mtsuelo=marchatsuelo,mtmin=marchatmin,mtmed=marchatmed,mtmax=marchatmax,tmax=tmax,tmin=tmin, rad=radiacion,pp=pp, temp= temp_suelo, temp2=temp_air, hum=humedad,hora=hour,date=date)



if __name__ == '__main__':
    app.run(debug=True)