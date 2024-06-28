import os
from datetime import timedelta
from quixstreams import Application

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(consumer_group="sentiment-average-v2.1", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

sdf = sdf[sdf.contains("party")]

sdf = sdf.group_by("party")

sdf = sdf[sdf["model_result"]["score"] > 0.8]

sdf = sdf.apply(lambda row: 1 if row["model_result"]["label"] == "POSITIVE" else -1)

sdf = sdf.hopping_window(timedelta(hours=1), timedelta(minutes=1), 5000).mean().final()

sdf = sdf.apply(lambda row, key, *_: {
    "average_sentiment_1h": row["value"],
    "timestamp": row["end"] * 1000000,
    "tags": {
        "party": key
    }
}, metadata=True)


sdf = sdf.update(lambda row: print(row))

sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)