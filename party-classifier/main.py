import os
from quixstreams import Application
from transformers import pipeline

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

# Load the zero-shot classification pipeline
classifier = pipeline("zero-shot-classification")
candidate_labels = ["Trump", "Biden"]


app = Application(consumer_group="party-classifier-v1", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

def select_party(row: dict):
    
    for i in range(len(row["labels"])):
        if row["scores"][i] > 0.7:
            return row["labels"][i]
    
    return "N/A"

sdf = app.dataframe(input_topic)

sdf = sdf[sdf["subreddit"] != "AskReddit"]

sdf["text"] = sdf.apply(lambda row: (row["title"] + "\n " + row["selftext"])[:512])
sdf["classification"] = sdf.apply(lambda row: classifier(row["text"], candidate_labels))

sdf["party"] = sdf["classification"].apply(select_party)
sdf = sdf.update(lambda row: print(f"{row['party']}: {row['text']}"))

sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)