import os
from quixstreams import Application
from transformers import pipeline
import json

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(consumer_group="transformation-v1", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

model_name = "distilbert-base-uncased-finetuned-sst-2-english"
print("Downloading {0} model...".format(model_name))
model_pipeline = pipeline(model=model_name)

sdf = app.dataframe(input_topic)

# Assuming the input data has a 'text' column that you want to process with the model
sdf['model_result'] = sdf['selftext'].apply(lambda text: json.dumps(model_pipeline(text)))
sdf = sdf.update(lambda row: print(row))

#sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)