import os
from datetime import timedelta
from quixstreams import Application, message_context
import datetime
# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(
    consumer_group="sentiment-average-v3.2", 
    auto_offset_reset="earliest",
    consumer_extra_config={
         'fetch.message.max.bytes': 1024 
    })

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

def transpose_model_results(row: dict):
    
    model_result = row["model_result"]
    
    confidence = model_result["confidence"]
    
    for key in model_result:
        if key == "confidence":
            continue
        
        yield {
            "name": key,
            "value": model_result[key],
            "confidence": confidence
        }

sdf = app.dataframe(input_topic)

sdf  = sdf.apply(transpose_model_results, expand=True)

sdf = sdf[sdf["confidence"] >= 0.5]

sdf = sdf.group_by("name").apply(lambda row: row["value"])

sdf = sdf.hopping_window(timedelta(days=1), timedelta(minutes=1), timedelta(minutes=1)).mean().final()

sdf = sdf.set_timestamp(lambda row, *_: row["end"])

sdf = sdf.apply(lambda row, key, *_: {
    "average_1h": row["value"],
    "timestamp": row["end"] * 1000000,
    "tags": {
        "metric": key
    }
}, metadata=True)

sdf = sdf.update(print)

sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)