import os

COMMAND = """
gcloud functions deploy {cloud_function_name}
--gen2 --runtime=python311 --region=us-east4
--source=. --entry-point={python_function_name}
--trigger-http --allow-unauthenticated
--env-vars-file env.yaml
""".replace("\n", " ").strip()

def deploy(cloud_function_name, python_function_name):
    command = COMMAND.format(cloud_function_name=cloud_function_name, python_function_name=python_function_name)
    os.system(command)

if __name__ == "__main__":
    os.system("gcloud config set project rivers-381716")

    deploy("chat", "chat")
    deploy("add_story", "add_story")
    deploy("get_stories", "get_stories")
