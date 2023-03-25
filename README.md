# Flask App for Compassionate Chatbot

This is a Flask app that serves as a chatbot utilizing GPT-3.5-turbo, Cohere embeddings, and Pinecone for vector indexing. The chatbot is designed to help people navigate and understand challenges in their lives by referencing stories from other people. The Flask app has three primary routes: adding stories, retrieving stories, and handling chat messages.

## Routes

### POST `/stories`

This route adds a new story to the index.

**Request:**

```json
{
  "story": "A story about a person overcoming a challenge in their life..."
}
```

**Response:**

```json
{
  "status": "success"
}
```

**Errors:**

- 400 Bad Request: No story provided.

### GET `/stories`

This route retrieves the top 3 stories relevant to a given query.

**Request:**

URL parameters:

- `query`: The query to find relevant stories (e.g., "dealing with anxiety at work")

**Response:**

```json
[
  {
    "story": "A story about a person dealing with anxiety at work...",
    "timestamp": 1628728394.503241
  },
  ...
]
```

**Errors:**

- 400 Bad Request: No query provided.

### POST `/chat`

This route handles chat messages and returns a response from the chatbot based on the provided messages and retrieved stories.

**Request:**

```json
{
  "messages": [
    {"role": "user", "content": "I'm feeling anxious at work. What can I do?"},
    {"role": "assistant", "content": "I understand that you're feeling anxious..."}
  ],
  "retrieved_stories": [
    {
      "story": "A story about a person dealing with anxiety at work...",
      "timestamp": 1628728394.503241
    },
    ...
  ]
}
```

**Response:**

```json
{
  "role": "assistant",
  "content": "Intimes of anxiety, it's important to remember..."
}
```

**Errors:**

- 400 Bad Request: `messages` is `null`. Please provide a list of messages in OpenAI API format.
- 400 Bad Request: `retrieved_stories` is `null`. Please provide a list of stories, even if empty.

## Usage

To use the Flask app, follow these steps:

1. Install the required packages:

   ```
   pip install flask openai cohere-sdk pinecone-client
   ```

2. Set up environment variables containing your API keys for OpenAI, Cohere, and Pinecone:

   ```
   export OPENAI_API_KEY=<your_openai_api_key>
   export COHERE_API_KEY=<your_cohere_api_key>
   export PINECONE_API_KEY=<your_pinecone_api_key>
   ```

3. Run the Flask app:

   ```
   python app.py
   ```

4. Use a tool like [Postman](https://www.postman.com/) or [curl](https://curl.se/) to interact with the Flask app routes.