import os

with open("functions/.env") as f:
    for line in f:
        var = line.strip().split("=")
        if len(var) == 2:
            os.environ[var[0]] = var[1]
