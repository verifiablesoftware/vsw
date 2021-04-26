from pathlib import Path

from flask import Flask, request, Response

app = Flask(__name__)


@app.route('/webhooks/', methods=['GET'])
def hello():
    print("Hello VSW")


@app.route('/webhooks/topic/connections/', methods=['POST'])
def connections():
    print(request.json)  # Handle webhook request here
    return Response(status=200)


@app.route('/webhooks/topic/present_proof/', methods=['POST'])
def present_proof():
    print(request.json)  # Handle webhook request here
    return Response(status=200)


@app.route("/webhooks/topic/issue_credential/", methods=['POST'])
def issue_credential():
    print(request.json)  # Handle webhook request here
    return Response(status=200)


@app.route("/webhooks/topic/problem_report/", methods=['POST'])
def problem_report():
    print(request.json)  # Handle webhook request here
    return Response(status=200)


def start_server():
    import logging
    log_dir = Path(__file__).parent.parent.parent.resolve()
    controller_log_file = str(Path(log_dir).joinpath("logs/controller.log").resolve())
    logging.basicConfig(filename=controller_log_file, level=logging.DEBUG)
    app.run(host='127.0.0.1', port=8022)
