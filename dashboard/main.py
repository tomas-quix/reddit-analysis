import streamlit as st
from influxdb_client_3 import Point, InfluxDBClient3
import pandas as pd
import plotly.express as px
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

# Streamlit app layout
st.title('Realtime US election Reddit analysis using ChatGPT')

# Add a radio button to select the time period
time_period = st.radio(
    "Select time period",
    ("Last 24 hours", "Last 1 week")
)

# Set the query based on the selected time period
if time_period == "Last 24 hours":
    query_time_interval = "24 hours"
else:
    query_time_interval = "7 days"

# Query InfluxDB
query = f'''
SELECT *
FROM "metrics-1day-mean"
WHERE time > now() - interval '{query_time_interval}'
ORDER BY time
'''

df = client.query(query=query, mode="pandas", language="sql")

# Plot the data using Plotly
fig = px.line(
    df, 
    x='time',
    y='average_1h', 
    color='metric',
    title=f'Analysis using ChatGPT for last {query_time_interval}',
    color_discrete_map={
        'Trump': 'red',
        'Biden': 'blue',
        'Trump_winning': '#FF9999',  # Light red
        'Biden_winning': '#9999FF'   # Light blue
    }
)

st.plotly_chart(fig)

# Update the words count query based on the selected time period
words_count_query = f'''
SELECT max(count) as "max", word, party
FROM "party-words-count"
WHERE time > now() - interval '{query_time_interval}' AND party != 'N/A'
GROUP BY word, party
'''

words_df = client.query(query=words_count_query, mode="pandas", language="sql")

def print_pie(df, party: str, column):
    df = df[df["party"] == party]

    aggregated_df = df.groupby('word')['max'].max().reset_index()
    sorted_df = aggregated_df.sort_values(by='max', ascending=False)

    fig = px.pie(sorted_df[:20], values='max', names='word', title=f'Most used words in last {query_time_interval} for ' + party)
    column.plotly_chart(fig)

# Create two columns for the pie charts
col1, col2 = st.columns(2)

with col1:
    print_pie(words_df, "Democrat", col1)

with col2:
    print_pie(words_df, "Conservative", col2)