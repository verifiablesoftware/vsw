import os
from pathlib import Path
from wsgiref.simple_server import make_server

from flask import Flask, request, Response
import logging

from vsw import utils

app = Flask(__name__)

log_folder = str(Path(os.path.expanduser('~')).joinpath("logs").resolve())
if not os.path.exists(log_folder):
    os.makedirs(log_folder)
controller_log_file = str(Path(os.path.expanduser('~')).joinpath("logs/vsw-controller.log").resolve())
logging.basicConfig(filename=controller_log_file, level=logging.DEBUG)


@app.route('/')
def hello():
    return "Hello VSW Controller"


@app.route('/webhooks/topic/connections/', methods=['POST'])
def connections():
    app.logger.info(request.json)
    return Response(status=200)


@app.route('/webhooks/topic/present_proof/', methods=['POST'])
def present_proof():
    app.logger.info(request.json)  # Handle webhook request here
    return Response(status=200)


@app.route("/webhooks/topic/issue_credential/", methods=['POST'])
def issue_credential():
    app.logger.info(request.json)  # Handle webhook request here
    return Response(status=200)


@app.route("/webhooks/topic/problem_report/", methods=['POST'])
def problem_report():
    app.logger.info(request.json)  # Handle webhook request here
    return Response(status=200)


if __name__ == '__main__':
    configuration = utils.get_vsw_agent()
    webhook_port = configuration.get("webhook_port")
    app.logger.info(f"started controller, http://127.0.0.1:{webhook_port}")
    server = make_server('127.0.0.1', int(webhook_port), app)
    server.serve_forever()
    app.run()