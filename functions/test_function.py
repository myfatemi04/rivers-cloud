import requests

result = requests.post("https://add-story-jxwxpho3rq-uk.a.run.app", json={"story": "Hello world"})
print(result)
print(result.status_code)
print(result.text)
