from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st
import requests
import datetime
#import matplotlib.pyplot as plt
#from bokeh.plotting import figure, output_file, show
#from bokeh.models import ColumnDataSource

"""
Little demo that is almost an URL builder app for the [ONC Oceans 3.0 API](https://wiki.oceannetworks.ca/display/O2A/Oceans+2.0+API+Home).


"""

try:
    query_params = st.experimental_get_query_params()
    #query_params
    token = query_params['token'][0]
except Exception as e:
    st.error('ONC API token required. Get yours at https://data.oceannetworks.ca/Profile')
    token = st.text_input('Enter your ONC API Token:', type="password")
    st.experimental_set_query_params(token=token)
    # e

# discover all BPRs
@st.cache(ttl=3600)
def getBPRdeployments(dC='BPR'):
    url = 'https://data.oceannetworks.ca/api/locations'
    params = {
        'token': token,
        'method': 'get',
        'deviceCategoryCode': dC,
        'locationCode': 'NEP',
        'includeChildren': 'true'
    }        
    r = requests.get(url, params=params)
    return r

p=getBPRdeployments()
sta = pd.DataFrame(p.json())[['locationCode', 'lon', 'lat', 'depth']]




 
@st.cache(ttl=3600)
def BPRData(locCode):
    url = 'https://data.oceannetworks.ca/api/scalardata'
    then = datetime.datetime.now()
    now = then-datetime.timedelta(seconds=3600*24)
    now = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    then = then.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
    params = {
        'token': token,
        'method': 'getByLocation',
        'locationCode':locCode,
        'deviceCategoryCode':'BPR',
        'dateFrom':now,
        'dateTo':then,
        'sensorCategoryCodes':'pressure'
    }
    
    r = requests.get(url, params=params)
    return r

locCodes =sta.locationCode.values
df=pd.DataFrame(columns=locCodes)
df.columns=locCodes

for locCode in locCodes:
    r=BPRData(locCode)
    data = r.json()
    #print(data)
            
    df[locCode]=(data['sensorData'][0]['data']['values'])
    #df = df.set_index(pd.to_datetime(df['sampleTimes']))
    #df['sampleTimes']=pd.to_datetime(df['sampleTimes'])
    #df = df.drop(columns=['qaqcFlags'])

df['sampleTimes']=pd.to_datetime(data['sensorData'][0]['data']['sampleTimes'])
df = df.set_index(df['sampleTimes'])
df = df.drop(columns='sampleTimes')
df
