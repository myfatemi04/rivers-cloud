import functions_framework

import hashlib
import os
import time

import cohere
import flask
import openai
import pinecone

# "unused" but loads env vars on import
import env

MODEL = 'gpt-3.5-turbo'

co = cohere.Client(os.environ['COHERE_API_KEY'])
pinecone.init(api_key=os.environ['PINECONE_API_KEY'], environment="us-west1-gcp")
openai.api_key = os.environ['OPENAI_API_KEY']

index = pinecone.Index("rivers")



def embed(string):
    return co.embed([string]).embeddings[0]

@functions_framework.http
def add_story():
    if 'story' not in flask.request.json:
        return flask.jsonify({'status': 'error', 'error': 'No story provided'}), 400

    story = flask.request.json['story']
    embedding = embed(story)
    vec_id = hashlib.sha256(story.encode()).hexdigest()
    index.upsert([
        (vec_id, embedding, {
            "story": story,
            "timestamp": time.time()
        })
    ])

    return {'status': 'success'}


@functions_framework.http
def get_stories():
    if 'query' not in flask.request.args:
        return flask.jsonify({'status': 'error', 'error': 'No query provided'}), 400

    query = flask.request.args['query']
    embedding = embed(query)
    result = index.query(vector=embedding, top_k=3, include_metadata=True)
    return [
        story['metadata']
        for story in result['matches']
    ]

@functions_framework.http
def chat():
    if 'messages' not in flask.request.json:
        return flask.jsonify({'status': 'error',
                              'error': '`messages` is `null`. Please provide a list of messages in OpenAI API format.'}), 400
    if 'retrieved_stories' not in flask.request.json:
        return flask.jsonify({'status': 'error',
                              'error': '`retrieved_stories` is `null`. Please provide a list of stories, even if empty.'}), 400

    messages = flask.request.json['messages']
    retrieved_stories = flask.request.json['retrieved_stories']

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
