from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st
import requests

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
 
@st.cache(ttl=3600)
def getDeviceCategories():
    url = 'https://data.oceannetworks.ca/api/deviceCategories'
    params = {
        'token': token,
        'method': 'get',
    }

    r = requests.get(url, params=params)
    return r
r_dc =  getDeviceCategories()
"Got device categories using: %s" % r_dc.url


device_categories = ['%s | %s' % (dc['deviceCategoryCode'], dc['deviceCategoryName']) for dc in r_dc.json()]
device_category = st.selectbox('Device Categories', device_categories)
'Selected device category: %s' % device_category

deviceCategoryCode = device_category.split(' | ')[0]

@st.cache(ttl=3600)
def getData(deviceCategoreyCode):
    url = 'https://data.oceannetworks.ca/api/locations'
    params = {
        'token': token,
        'method': 'get',
        'deviceCategoryCode': deviceCategoryCode,
        'locationCode': 'NEP',
        'includeChildren': 'true'
    }

    r = requests.get(url, params=params)
    return r

r = getData(deviceCategoryCode)    

r.url

#st.json(r.json())

sta = pd.DataFrame(r.json())[['locationCode', 'lon', 'lat', 'depth']]
sta

def convert_df(df):
   return df.to_csv().encode('utf-8')


csv = convert_df(sta)

st.download_button(
   "Press to Download",
   csv,
   "file.csv",
   "text/csv",
   key='download-csv'
)

st.map(sta)

"""
# Welcome to Streamlit!

Edit `/streamlit_app.py` to customize this app to your heart's desire :heart:

If you have any questions, checkout our [documentation](https://docs.streamlit.io) and [community
forums](https://discuss.streamlit.io).

In the meantime, below is an example of what you can do with just a few lines of code:
"""


with st.echo(code_location='below'):
    total_points = st.slider("Number of points in spiral", 1, 5000, 2000)
    num_turns = st.slider("Number of turns in spiral", 1, 100, 9)

    Point = namedtuple('Point', 'x y')
    data = []

    points_per_turn = total_points / num_turns

    for curr_point_num in range(total_points):
        curr_turn, i = divmod(curr_point_num, points_per_turn)
        angle = (curr_turn + 1) * 2 * math.pi * i / points_per_turn
        radius = curr_point_num / total_points
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        data.append(Point(x, y))

    st.altair_chart(alt.Chart(pd.DataFrame(data), height=500, width=500)
        .mark_circle(color='#0068c9', opacity=0.5)
        .encode(x='x:Q', y='y:Q'))
