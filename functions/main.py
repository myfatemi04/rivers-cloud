import functions_framework

import hashlib
import os
import time
import requests
import json
from operator import itemgetter

import cohere
import flask
import openai
import pinecone

MODEL = os.environ.get("MODEL", 'gpt-3.5-turbo')

co = cohere.Client(os.environ['COHERE_API_KEY'])
pinecone.init(api_key=os.environ['PINECONE_API_KEY'], environment="us-west1-gcp")
openai.api_key = os.environ['OPENAI_API_KEY']

index = pinecone.Index("rivers")

emotion_inference_model = os.environ.get("SENTIMENT_MODEL", "j-hartmann/emotion-english-distilroberta-base")
hf = os.environ["HUGGINGFACE_API_KEY"]

def embed(string):
    return co.embed([string]).embeddings[0]

# CORS decorator
def cors(function):
    def wrapper(request):
        if request.method == 'OPTIONS':
            # preflight request
            headers = {}
            headers['Access-Control-Allow-Origin'] = '*'
            headers['Access-Control-Allow-Headers'] = 'Content-Type'
            headers['Access-Control-Max-Age'] = '3600'
            return ('', 204, headers)

        response = function(request)
        if type(response) is tuple:
            if len(response) == 2:
                response, status = response
                headers = {}
            else:
                response, status, headers = response
        else:
            status = 200
            headers = {}
        headers['Access-Control-Allow-Origin'] = '*'
        return (response, status, headers)
    return wrapper

def analyze_emotion(string):
    headers = {"Authorization": f"Bearer {hf}"}
    url = "https://api-inference.huggingface.co/models/" + emotion_inference_model

    def query(payload):
        data = json.dumps(payload)
        response = requests.request("POST", url, headers=headers, data=data)
        return json.loads(response.content.decode("utf-8"))

    try:
        data = query({"inputs": string})[0]
        return sorted(data, key=itemgetter('score'))[-1]['label']
    except:
        return "neutral"

@functions_framework.http
@cors
def add_story(request):
    if 'story' not in request.json:
        return flask.jsonify({'status': 'error', 'error': 'No story provided'}), 400

    story = request.json['story']
    embedding = embed(story)
    vec_id = hashlib.sha256(story.encode()).hexdigest()
    index.upsert([
        (vec_id, embedding, {
            "story": story,
            "timestamp": time.time(),
            "emotion": analyze_emotion(story)
        })
    ])

    return {'status': 'success'}


@functions_framework.http
@cors
def get_stories(request):
    if 'query' not in request.args:
        return flask.jsonify({'status': 'error', 'error': 'No query provided'}), 400

    query = request.args['query']
    embedding = embed(query)
    result = index.query(vector=embedding, top_k=3, include_metadata=True)
    return [
        story['metadata']
        for story in result['matches']
    ]

def get_quote(story, most_recent_ai_message):
    result = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a chatbot designed to extract relevant quotes from stories."},
            {"role": "system", "content": f"Story:\n\n{story}"},
            {"role": "user", "content": f"{most_recent_ai_message}\n\n---\n\nProvide a helpful quote (1-3 sentences) from the story that supports the above message. Only write the quote, do not explain."},
        ]
    )
    return result.choices[0].message['content']

@functions_framework.http
@cors
def chat(request):
    if 'messages' not in request.json:
        return flask.jsonify({'status': 'error',
                              'error': '`messages` is `null`. Please provide a list of messages in OpenAI API format.'}), 400
    if 'retrieved_stories' not in request.json:
        return flask.jsonify({'status': 'error',
                              'error': '`retrieved_stories` is `null`. Please provide a list of stories, even if empty.'}), 400

    messages = request.json['messages']
    retrieved_stories = request.json['retrieved_stories']

    messages_with_prompt = [
        {"role": "system",
         "content": "You are a compassionate chatbot designed to help people navigate and understand challenges in their lives. You will be provided stories from other people. Reference these by number in square brackets (i.e., [3]) at the end of sentences where you think they are helpful."}
    ]
    for i, story in enumerate(retrieved_stories):
        messages_with_prompt.append({"role": "system", "content": f"Story {i + 1}:\n\n{story['story']}"})
        messages_with_prompt.append({"role": "system", "content": f"A new user has arrived."})
    messages_with_prompt.extend(messages)

    completion = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages_with_prompt,
    )
    message = completion.choices[0].message

    quotes = [None] * 3

    for i in [1, 2, 3]:
        if f"[{i}]" in message['content']:
            quotes[i - 1] = get_quote(retrieved_stories[i - 1]['story'], message['content'])

    return {"message": dict(message), "quotes": quotes}


if __name__ == '__main__':
    pass
