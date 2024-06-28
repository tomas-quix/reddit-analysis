import streamlit as st
from influxdb_client_3 import Point, InfluxDBClient3
import pandas as pd
import plotly.express as px
import datetime
import os
from streamlit_autorefresh import st_autorefresh

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

# Set the page layout to wide
st.set_page_config(layout="wide")

# Automatically refresh the page every minute (60,000 ms)
st_autorefresh(interval=60000, key="datarefresh")

# Initialize InfluxDB client
client = InfluxDBClient3(token=os.environ["INFLUXDB_TOKEN"],
                         host=os.environ["INFLUXDB_HOST"],
                         org=os.environ["INFLUXDB_ORG"],
                         database=os.environ["INFLUXDB_DATABASE"])

# Query InfluxDB
query = '''
SELECT *
FROM "party-sentiment-average-1day"
WHERE time > now() - interval '24 hours' AND party != 'N/A'
ORDER BY time
'''

df =  client.query(query=query,
                   mode="pandas",
                   language="sql")


# # Plot the data using Plotly
fig = px.line(
    df, 
    x='time',
    y='average_sentiment_1h', 
    color='party',
    title='Analysis of Reddit regarding US election for last 24 hours',
    color_discrete_map={
                  'Conservative': 'red',
                  'Democrat': 'blue'
              })



# Streamlit app layout
st.title('Realtime US election Reddit analysis')
st.write('This dashboard visualizes the sentiment average over the last 24 hours displaying 24 hours rolling average updated every minute.')

st.plotly_chart(fig)


words_count_query = '''
SELECT max(count) as "max", word, party
FROM "party-words-count"
WHERE time > now() - interval '24 hours' AND party != 'N/A'
GROUP BY word, party
'''

words_df =  client.query(query=words_count_query,
                   mode="pandas",
                   language="sql")

def print_pie(df, party: str, column):
    df = df[df["party"] == party]

    aggregated_df = df.groupby('word')['max'].max().reset_index()

    sorted_df = aggregated_df.sort_values(by='max', ascending=False)


    fig = px.pie(sorted_df[:20], values='max', names='word', title='Most used words in last 24 hours for ' + party)
    column.plotly_chart(fig)
    
    # Create two columns for the pie charts
col1, col2 = st.columns(2)

with col1:
    print_pie(words_df, "Democrat", col1)

with col2:
    print_pie(words_df, "Conservative", col2)
    