from quixstreams import Application
from praw import Reddit
from praw.exceptions import APIException

import os
import json
import time

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

subreddits = os.environ["subreddits"].split(",")

# Replace the following values with your Reddit app credentials
client_id = os.environ["client_id"]
client_secret = os.environ["client_secret"]
user_agent = 'quix-source-v1'

# Initialize the Reddit instance
reddit = Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent)

# Listen to multiple subreddits in real-time
subreddit_stream = reddit.subreddit('+'.join(subreddits))

print("Listening to new posts from the specified subreddits...")

def process_submission(post, producer):
    while True:
        try:
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
            
            # publish the data to the topic
            producer.produce(
                topic=topic.name,
                key=msg['subreddit'],
                value=json_data,
                timestamp=int(msg["created_utc"] * 1000)
            )
            break
        except APIException as e:
            if e.error_type == 'RATELIMIT':
                print("Rate limit exceeded, sleeping for 60 seconds...")
                time.sleep(60)
            else:
                raise

app = Application()  # create an Application

# define the topic using the "output" environment variable
topic_name = os.environ["output"]
topic = app.topic(topic_name)

if __name__ == "__main__":
    try:
        with app.get_producer() as producer:
            for post in subreddit_stream.stream.submissions(skip_existing=False):
                process_submission(post, producer)
    except KeyboardInterrupt:
        print(f"Stopped listening.")
    except Exception as e:
        print(f"An error occurred: {e}")

