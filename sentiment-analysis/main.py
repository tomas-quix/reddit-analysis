import os
from quixstreams import Application
from transformers import pipeline
import json

# Load environment variables (useful when working locally)
from dotenv import load_dotenv
load_dotenv()



app = Application(consumer_group="hugging-face-model-v1.2", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

# Download the Hugging Face model (list of available models here: https://huggingface.co/models)
# suggested default is distilbert-base-uncased-finetuned-sst-2-english
classifier = pipeline('sentiment-analysis')

sdf = app.dataframe(input_topic)

# Assuming the input data has a 'text' column that you want to process with the model
sdf['model_result'] = sdf.apply(lambda row: classifier((row["title"] + "\n " + row["selftext"])[:512])[0])

sdf = sdf.update(print)

# Send the processed data to the output topic
sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)