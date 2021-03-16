import os
import subprocess
from pyngrok import ngrok
from vsw.commands import register



def test_public_ip():
    register.get_public_url()

def test_commands():
    res = os.system("ssh -R 80:localhost:8020 localhost.run >> out.log")
    print(res)


def test_ngrok():
    # Open a HTTP tunnel on the default port 80
    # <NgrokTunnel: "http://<public_sub>.ngrok.io" -> "http://localhost:80">
    # http_tunnel = ngrok.connect(8020)

    ngrok_process = ngrok.get_ngrok_process()

    try:
        # Block until CTRL-C or some other terminating event
        ngrok_process.proc.wait()
    except KeyboardInterrupt:
        print(" Shutting down server.")
        ngrok.kill()


def test_get_tunnel():
    tunnels = ngrok.get_tunnels()
    print(tunnels)