from quixstreams import Application  # Import the Quix Streams modules for interacting with Kafka
import os
import json
import time
from praw import Reddit
from praw.exceptions import APIException
from dotenv import load_dotenv  # For local dev, load env vars from a .env file

# Load environment variables from .env file
load_dotenv()

# Retrieve subreddit names and Reddit app credentials from environment variables
subreddits = os.environ["subreddits"].split(",")
client_id = os.environ["client_id"]
client_secret = os.environ["client_secret"]
user_agent = 'quix-source-v1'

# Initialize the Reddit instance
reddit = Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent
)

# Combine subreddit names into a single string for streaming
subreddit_stream = reddit.subreddit('+'.join(subreddits))

print("Listening to new posts from the specified subreddits...")

# Create an Application instance
app = Application()

# Define the topic using the "output" environment variable
topic_name = os.environ["output"]
topic = app.topic(topic_name)

def process_submission(producer, post):
    """Process and publish a new Reddit submission."""
    msg = {
        'title': post.title,
        'author': str(post.author),
        'url': post.url,
        'created_utc': post.created_utc,
        'score': post.score,
        'id': post.id,
        'subreddit': post.subreddit.display_name,
        'selftext': post.selftext
    }

    json_data = json.dumps(msg, indent=4)
    print(json_data)

    # Publish the data to the topic
    producer.produce(
        topic=topic.name,
        key=msg['subreddit'],
        value=json_data,
        timestamp=int(msg["created_utc"] * 1000)
    )

if __name__ == "__main__":
    with app.get_producer() as producer:
        try:
            for post in subreddit_stream.stream.submissions(skip_existing=False):
                process_submission(producer, post)
        except APIException as e:
            if e.error_type == 'RATELIMIT':
                print("Rate limit exceeded, sleeping for 60 seconds...")
                time.sleep(60)
            else:
                raise
        except KeyboardInterrupt:
            print("Stopped listening.")
        except Exception as e:
            print(f"An error occurred: {e}")