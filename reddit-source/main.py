from quixstreams import Application  # import the Quix Streams modules for interacting with Kafka:

import os
import json
import threading
from praw import Reddit
from praw.exceptions import APIException
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

# Function to listen to a subreddit
def listen_to_subreddit(subreddit_name, producer):
    subreddit = reddit.subreddit(subreddit_name)
    print(f"Listening to new posts in r/{subreddit_name}...")
    while True:
        try:
            for post in subreddit.stream.submissions():
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
        except APIException as e:
            if e.error_type == 'RATELIMIT':
                print("Rate limit exceeded, sleeping for 60 seconds...")
                time.sleep(60)
            else:
                raise
        except KeyboardInterrupt:
            print(f"Stopped listening to r/{subreddit_name}.")
            break
    
app = Application()  # create an Application

# define the topic using the "output" environment variable
topic_name = os.environ["output"]
topic = app.topic(topic_name)


if __name__ == "__main__":
    try:
         # create a pre-configured Producer object.
        with app.get_producer() as producer:
            
            # Start a thread for each subreddit
            threads = []
            for subreddit_name in subreddits:
                thread = threading.Thread(target=listen_to_subreddit, args=(subreddit_name, producer))
                thread.start()
                threads.append(thread)

            # Join threads to main thread
            for thread in threads:
                thread.join()
                
              

        print("All rows published")
    except KeyboardInterrupt:
        print("Exiting.")