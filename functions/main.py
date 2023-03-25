import functions_framework

import hashlib
import os
import time
import requests
import json

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
    API_URL = "https://api-inference.huggingface.co/models/" + emotion_inference_model

    def query(payload):
        data = json.dumps(payload)
        response = requests.request("POST", API_URL, headers=headers, data=data)
        return json.loads(response.content.decode("utf-8"))

    return query({"inputs": string})

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
            # "sentiment": analyze_emotion(story)
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
         "content": "You are a compassionate chatbot designed to help people navigate and understand challenges in their lives. You will be provided stories from other people to reference in your responses to the user's messages."}
    ]
    for i, story in enumerate(retrieved_stories):
        messages_with_prompt.append({"role": "system", "content": f"Story {i + 1}:\n\n{story['story']}"})
    messages_with_prompt.extend(messages)

    completion = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages_with_prompt,
    )
    message = completion.choices[0].message

    return flask.jsonify(message)


if __name__ == '__main__':
    pass
