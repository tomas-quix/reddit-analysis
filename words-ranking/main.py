import os
from quixstreams import Application
from datetime import timedelta, datetime
import uuid
import re
import certifi

import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import uuid


import nltk
from nltk.corpus import stopwords
from nltk import word_tokenize, pos_tag, ne_chunk

# Set up certifi for macOS SSL issues
try:
    import certifi
    os.environ['SSL_CERT_FILE'] = certifi.where()
except ImportError:
    pass

# Function to download stopwords with a fallback for manual download
def download_resources():
    try:
        nltk.download('stopwords')
        nltk.download('averaged_perceptron_tagger')
        nltk.download('maxent_ne_chunker')
        nltk.download('words')
    except Exception as e:
        print("Error downloading resources:", e)

# Download stopwords and necessary NLTK resources
download_resources()
stop_words = set(stopwords.words('english'))

# Add additional plain English words to stopwords list
additional_stopwords = set(["thing", "seen", "like", "said", "will", "get", "make", "would"])
stop_words.update(additional_stopwords)

# Function to classify words using POS tagging and NER, and yield only content words
def classify_words(row):
    words = word_tokenize(row["text"])
    pos_tags = pos_tag(words)
    named_entities = ne_chunk(pos_tags)
    
    # Extract named entities
    for chunk in named_entities:
        if hasattr(chunk, 'label') and chunk.label():
            entity = ' '.join(c[0] for c in chunk)
            yield {
                "word": entity,
                "party": row["party"]
            }
    
    for word, tag in pos_tags:
        if word.lower() not in stop_words and tag.startswith(('NN', 'VB')):
            yield {
                "word": word,
                "party": row["party"]
            }
    

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application(consumer_group=str(uuid.uuid4()), auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"], key_serializer='json')

sdf = app.dataframe(input_topic)

sdf = sdf[sdf["party"] != "N/A"]

sdf["text"] = sdf.apply(lambda row: (row["title"] + "\n " + row["selftext"])[:512])
        
sdf = sdf.apply(classify_words, expand=True)

sdf = sdf.group_by(lambda row: row, name="words-per-party")

sdf = sdf.apply(lambda row: row["word"])

sdf = sdf.hopping_window(timedelta(hours=1), timedelta(minutes=5), timedelta(minutes=1)).count().final()

sdf["timestamp"] = sdf["end"] * 1000000
sdf["count"] = sdf["value"]
sdf["tags"] = sdf.apply(lambda row, key, *_: key,metadata=True)

sdf = sdf[["timestamp", "count", "tags"]]

sdf = sdf.update(lambda row, key, *_: print(f"{key}:{row}"), metadata=True)

sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)