# import requests

# result = requests.post("https://add-story-jxwxpho3rq-uk.a.run.app", json={"story": "Hello world"})
# print(result)
# print(result.status_code)
# print(result.text)

# import functions.main
import env

import openai

def get_quote(story, most_recent_ai_message):
    result = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {"role": "system", "content": "You are a chatbot designed to extract relevant quotes from stories."},
            {"role": "system", "content": f"Story:\n\n{story}"},
            {"role": "user", "content": f"{most_recent_ai_message}\n\n---\n\nProvide a quote (1-3 sentences) from the story that supports the above message. Only write the quote, do not explain."},
        ]
    )
    return result.choices[0].message['content']

q = get_quote(story="I used to have a lot of anxiety about tests. However, I found that breaking my studying into really small chunks helped me out a lot.", most_recent_ai_message="""I'm sorry to hear that you're feeling anxious about your exams. It's understandable to feel that way, but it's important to remember that you can do things to manage that anxiety. 

As [1] mentioned, breaking your studying into smaller chunks can be helpful. This can help you feel less overwhelmed and more in control. Additionally, try to identify if there are any specific areas or topics that you feel particularly anxious about, and prioritize those in your studying.""")

print("Quote:", q)
