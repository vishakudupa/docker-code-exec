import docker
from flask import Flask
import flask
from flask import request
import subprocess
import shlex
import os
client = docker.from_env()

LANGUAGE = 'language'
ID = 'id'

app = Flask(__name__)

JAVA_DOCKER_TEMPLATE = """ 
FROM openjdk:8
COPY . /usr/src/myapp
WORKDIR /usr/src/myapp
RUN javac CodePost.java
CMD ["java", "CodePost"]
"""

CPP_DOCKER_TEMPLATE = """
FROM gcc:4.9
COPY . /usr/src/cpp
WORKDIR /usr/src/cpp
RUN g++ -o CPP Cpp.cpp
CMD ["./CPP"]
"""

PYTHON_DOCKER_TEMPLATE = """
FROM python:3
COPY . /usr/src/cpp
WORKDIR /usr/src/cpp
CMD [ "python", "./py_script.py" ]
"""

OUTPUT_TEMPLATE = """## Result
```
<blockquote>
{1}
<blockquote>
```
"""


def write_to_file(path, content):
    f = open(path, "w")
    f.write(str(content))
    f.close()


def create_docker_file(args):
    path = './' + args[LANGUAGE] + "/" + args[ID] + "/" + "Dockerfile"
    if (args[LANGUAGE] == 'java'):
        write_to_file(path, JAVA_DOCKER_TEMPLATE)
    if (args[LANGUAGE] == 'python'):
        write_to_file(path, PYTHON_DOCKER_TEMPLATE)
    if (args[LANGUAGE] == 'cpp'):
        write_to_file(path, CPP_DOCKER_TEMPLATE)


def create_source_file(args, code):

    if (args[LANGUAGE] == 'java'):
        path = './' + args[LANGUAGE] + "/" + args[ID] + "/" + "CodePost.java"
        write_to_file(path, code)
    if (args[LANGUAGE] == 'python'):
        path = './' + args[LANGUAGE] + "/" + args[ID] + "/" + "py_script.py"
        write_to_file(path, code)
    if (args[LANGUAGE] == 'cpp'):
        path = './' + args[LANGUAGE] + "/" + args[ID] + "/" + "Cpp.cpp"
        write_to_file(path, code)


def get_output(args, code):
    # try:
    path = "./" + args[LANGUAGE] + "/" + args[ID]
    if not os.path.exists(path):
        os.makedirs(path)
    create_docker_file(args)
    create_source_file(args, code.decode("utf-8"))
    build = client.images.build(path=path)
    output = client.containers.run(build[0].id, remove=True)
    return OUTPUT_TEMPLATE.format(output.decode("utf-8"))
    # except:
    #     return "error"


@app.route('/', methods=['POST'])
def run_program():
    resp = flask.Response(get_output(request.args, request.data))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.content_type = 'application/json'
    return resp


app.run(debug=False)
