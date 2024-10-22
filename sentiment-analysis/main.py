import os
from quixstreams import Application
import json
import uuid
# Load environment variables (useful when working locally)
from dotenv import load_dotenv
load_dotenv()
import datetime
import openai

# Set up the OpenAI API key
openai.api_key = os.environ["openai_key"]

app = Application(consumer_group="chat-gpt-v1", auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
output_topic = app.topic(os.environ["output"])

# Function to update real-time data
def update_data(row):
    
    comment = row["title"]
    
    prompt = f"""
Analyze the sentiment of the following text: {comment}.
Provide a sentiment score between -1 (very negative) and 1 (very positive) for Trump and Biden. 
Judge also based on this text, chance of winning for both from -1 (losing) to 1 (winning).
At any moment don't deviate from JSON schema and don't add any notes, just return JSON. 
Provide the sentiment scores in the following JSON format:
{{
    "Trump": <sentiment_score>, 
    "Biden": <sentiment_score>, 
    "Trump_winning": <trump_winning_score>,
    "Biden_winning": <biden_winning_score>,
    "confidence": <confidence>
    }}.
"""
    
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a sentiment analysis model."},
            {"role": "user", "content": prompt}],
        max_tokens=512,
        n=1,
        stop=None,
        temperature=0.5,
    )
    response_content = response.choices[0].message.content
    
    try:
        json_start = response_content.find('{')
        json_end = response_content.rfind('}') + 1
        json_content = response_content[json_start:json_end]
        
        return json.loads(json_content)
        
    except Exception as ex:
        print("ERROR in parsing ChatGPT response.")
        print(json_content)
        raise
    


sdf = app.dataframe(input_topic)


#keywords = ["trump", "biden","democrats", "republicans", "campaign", "debate", "election"]

#sdf = sdf.filter(lambda row: any(keyword.lower() in row["title"] for keyword in keywords))


# Assuming the input data has a 'text' column that you want to process with the model
sdf['model_result'] = sdf.apply(update_data)

sdf = sdf.update(print)

# Send the processed data to the output topic
sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)