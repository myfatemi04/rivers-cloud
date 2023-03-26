import os
import subprocess

COMMAND = """
gcloud functions deploy {cloud_function_name}
--gen2 --runtime=python311 --region=us-east4
--source=. --entry-point={python_function_name}
--trigger-http --allow-unauthenticated
--env-vars-file env.yaml
""".replace("\n", " ").strip()

SHELL_DIR='/bin/zsh'
def deploy(cloud_function_name, python_function_name):
    command = COMMAND.format(cloud_function_name=cloud_function_name, python_function_name=python_function_name)
    # os.system(command)
    subprocess.call(command, shell=True, executable=SHELL_DIR)

if __name__ == "__main__":
    command = "gcloud config set project rivers-381716"
    subprocess.call(command, shell=True, executable=SHELL_DIR)

    deploy("add_story", "add_story")
    deploy("get_stories", "get_stories")
    deploy("chat", "chat")
