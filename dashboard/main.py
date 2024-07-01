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

st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 1rem;  /* Adjust this value as needed */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Add custom CSS to reduce the white space at the top of the page and style the title
st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 1rem;  /* Adjust this value as needed */
    }
    .title-container {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;  /* Align items to the top */
    }
    .title-container svg {
        margin-left: 10px;  /* Adjust this value as needed */
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Streamlit app layout with text on the left and SVG logo on the right
st.markdown(
    """
    <div class="title-container">
        <div>
            <h1>US election real-time analysis</h1>
            <h3>Subtitle goes here</h3>
        </div>
        <svg id="Layer_2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 288.57" width="150">
            <g id="Layer_1-2">
                <g>
                    <rect x="118.03" y="118.03" width="52.46" height="52.46" fill="#0064ff"></rect>
                    <rect x="177.05" y="177.05" width="52.46" height="52.46" rx="7.87" ry="7.87" fill="#bd2eff"></rect>
                    <circle cx="258.36" cy="258.36" r="30.16" fill="#ff7828"></circle>
                    <path d="M283.28,0H5.25C2.35,0,0,2.35,0,5.25V283.28c0,2.9,2.35,5.25,5.25,5.25H165.25c2.9,0,5.25-2.35,5.25-5.25v-41.97c0-2.9-2.35-5.25-5.25-5.25H52.46V52.46H236.07v113.07c0,2.9,2.35,5.25,5.25,5.25h41.97c2.9,0,5.25-2.35,5.25-5.25V5.25c0-2.9-2.35-5.25-5.25-5.25Zm301.68,118.08h-42.05c-2.9,0-5.25,2.35-5.25,5.25v160c0,2.9,2.35,5.25,5.25,5.25h42.05c2.9,0,5.25-2.35,5.25-5.25V123.32c0-2.9-2.35-5.25-5.25-5.25Zm0-91.89h-42.05c-2.9,0-5.25,2.35-5.25,5.25v42.05c0,2.9,2.35,5.25,5.25,5.25h42.05c2.9,0,5.25-2.35,5.25-5.25V31.43c0-2.9-2.35-5.25-5.25-5.25Zm-91.73,91.89h-42.05c-2.9,0-5.25,2.35-5.25,5.25v112.7h-65.63V123.28c0-2.9-2.35-5.25-5.25-5.25h-42.05c-2.9,0-5.25,2.35-5.25,5.25l.22,160.05c0,2.89,2.35,5.24,5.25,5.24h160.01c2.9,0,5.25-2.35,5.25-5.25V123.32c0-2.9-2.35-5.25-5.25-5.25Zm306.77,5.2c0-2.9-2.35-5.25-5.25-5.25h-41.97c-2.9,0-5.25,2.35-5.25,5.25v34.1l-32.79,21.86-32.79-21.86v-34.1c0-2.9-2.35-5.25-5.25-5.25h-41.97c-2.9,0-5.25,2.35-5.25,5.25v47.21l49.18,32.79-49.18,32.79v47.21c0,2.9,2.35,5.25,5.25,5.25h41.97c2.9,0,5.25-2.35,5.25-5.25v-34.45l32.6-21.63,32.98,21.98v34.1c0,2.9,2.35,5.25,5.25,5.25h41.97c2.9,0,5.25-2.35,5.25-5.25v-47.21l-49.29-32.86,49.29-32.71v-47.21Z" fill="#14174d"></path>
                </g>
            </g>        
        </svg>
    </div>
    """,
    unsafe_allow_html=True
)


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
FROM "metrics-1day-rolling-average"
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

# Add a text block at the bottom with a link to a GitHub repo
st.markdown(
    """
    For more details, visit our [GitHub repository]().
    """
)

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

    # the data was originally setup to use Conservatie instead of Republican
    display_party = "Conservative" if party == "Republican" else party
    fig = px.pie(sorted_df[:20], values='max', names='word', title=f'Most used words in last {query_time_interval} for ' + display_party)
    column.plotly_chart(fig)

# Create two columns for the pie charts
col1, col2 = st.columns(2)

with col1:
    print_pie(words_df, "Democrat", col1)

with col2:
    print_pie(words_df, "Republican", col2)
