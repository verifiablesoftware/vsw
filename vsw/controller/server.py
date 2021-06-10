import logging
import os
from multiprocessing.connection import Client
from pathlib import Path
from wsgiref.simple_server import make_server
from vsw.dao import vsw_dao
from flask import Flask, request, Response

from vsw import utils
from vsw.utils import Constant
app = Flask(__name__)

log_folder = str(Path(os.path.expanduser('~')).joinpath("vsw_logs").resolve())
if not os.path.exists(log_folder):
    os.makedirs(log_folder)
controller_log_file = str(Path(os.path.expanduser('~')).joinpath("vsw_logs/vsw-controller.log").resolve())
logging.basicConfig(filename=controller_log_file, level=logging.DEBUG)


@app.route('/')
def hello():
    return "Welcome to vsw controller"


@app.route('/webhooks/topic/connections/', methods=['POST'])
def connections():
    app.logger.info("=======/webhooks/topic/connections/ START===========")
    app.logger.info(request.json)
    app.logger.info("=======/webhooks/topic/connections/ END===========")
    address = ('localhost', Constant.PORT_NUMBER)
    conn = Client(address)
    conn.send(request.json)
    conn.close()
    return Response(status=200)


@app.route("/webhooks/topic/issue_credential/", methods=['POST'])
def issue_credential():
    app.logger.info("=======/webhooks/topic/issue_credential/ START===========")
    app.logger.info(request.json)  # Handle webhook request here
    app.logger.info("=======/webhooks/topic/issue_credential/ END===========")
    save_credential(request.json)
    address = ('localhost', Constant.PORT_NUMBER)
    conn = Client(address)
    conn.send(request.json)
    return Response(status=200)


@app.route('/webhooks/topic/present_proof/', methods=['POST'])
def present_proof():
    app.logger.info("=======/webhooks/topic/present_proof/ START===========")
    app.logger.info(request.json)  # Handle webhook request here
    app.logger.info("=======/webhooks/topic/present_proof/ END===========")
    address = ('localhost', Constant.PORT_NUMBER)
    conn = Client(address)
    conn.send(request.json)
    return Response(status=200)


@app.route("/webhooks/topic/problem_report/", methods=['POST'])
def problem_report():
    app.logger.info("=======/webhooks/topic/problem_report/ START===========")
    app.logger.info(request.json)  # Handle webhook request here
    app.logger.info("=======/webhooks/topic/problem_report/ END===========")
    address = ('localhost', Constant.PORT_NUMBER)
    conn = Client(address)
    conn.send(request.json)
    return Response(status=200)


@app.route("/webhooks/topic/revocation_registry/", methods=['POST'])
def revocation_registry():
    app.logger.info("=======/webhooks/topic/revocation_registry/ START===========")
    app.logger.info(request.json)  # Handle webhook request here
    app.logger.info("=======/webhooks/topic/revocation_registry/ END===========")
    return Response(status=200)


@app.route("/webhooks/topic/issuer_cred_rev/", methods=['POST'])
def issuer_cred_rev():
    app.logger.info("=======/webhooks/topic/issuer_cred_rev/ START===========")
    app.logger.info(request.json)  # Handle webhook request here
    app.logger.info("=======/webhooks/topic/issuer_cred_rev/ END===========")
    return Response(status=200)


@app.route("/webhooks/topic/basicmessages/", methods=['POST'])
def basicmessages():
    app.logger.info("=======/webhooks/topic/basicmessages/ START===========")
    app.logger.info(request.json)  # Handle webhook request here
    app.logger.info("=======/webhooks/topic/basicmessages/ END===========")
    return Response(status=200)


@app.route("/webhooks/topic/ping/", methods=['POST'])
def ping():
    app.logger.info(request.json)  # Handle webhook request here
    return Response(status=200)


if __name__ == '__main__':
    configuration = utils.get_vsw_agent()
    webhook_port = configuration.get("webhook_port")
    app.logger.info(f"Started controller, http://127.0.0.1:{webhook_port}")
    server = make_server('127.0.0.1', int(webhook_port), app)
    server.serve_forever()
    app.run()


def save_credential(msg):
    state = msg["state"]
    if state == 'credential_acked':
        credential = msg["credential"]
        revocation_id = msg.get("revocation_id", '')
        values = credential["values"]
        attrs = {}
        for key, value in values.items():
            attrs[key] = value.get("raw", "")
        content = {
            "schema_id": credential["schema_id"],
            "cred_def_id": credential["cred_def_id"],
            "rev_reg_id": credential["rev_reg_id"],
            "cred_rev_id": revocation_id,
            "attrs": attrs
        }
        issuer_did = attrs.get("developerDid", "")
        software_name = attrs.get("softwareName", "")
        software_did = attrs.get("softwareDid", "")
        vsw_dao.save_credential(issuer_did, software_name, software_did, "success", content)
