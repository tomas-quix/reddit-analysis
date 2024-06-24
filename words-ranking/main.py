import os
from quixstreams import Application
from datetime import timedelta, datetime
import uuid
import re

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(consumer_group="words-count-v1.3", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

def split_words(row: dict):
    for word in re.findall(r'\b\w+\b', row["selftext"]):
        yield word
        
sdf = sdf.apply(split_words, expand=True)

sdf = sdf.group_by(lambda row: row, name="word")

sdf = sdf.hopping_window(timedelta(hours=1), timedelta(minutes=5), timedelta(minutes=1)).count().final()

sdf["timestamp"] = sdf["end"] * 1000000
sdf["count"] = sdf["value"]
sdf["tags"] = sdf.apply(lambda row, key, _: {
    "word": key
},metadata=True)

sdf = sdf[["timestamp", "count", "tags"]]

sdf = sdf.update(lambda row, key, _: print(f"{key}:{row}"), metadata=True)

sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)