# This file should be outside of the /my_app directory
import docker
client = docker.from_env()
image, logs = client.images.build(path="/home/skaufma/PycharmProjects/proj2_main_app/my_app/", tag="proj2-main-flask-app:1.0.7")
for line in logs:
    print(line)