import os
import sys
import json
import logging
import socket
from flask import Blueprint, render_template, request

bp = Blueprint('bp', __name__, template_folder='templates')
HOST = os.getenv('SEND_HOST')
PORT = int(os.getenv('SEND_PORT'))


def read_form_data():
    with open('/app/form_data.json') as f:
        data = json.load(f)
        return data


@bp.route('/', methods=['GET', 'POST'])
def home():
    data = read_form_data()

    if request.method == 'POST':
        results = request.form.keys()
        for r in results:
            for k, v in data.items():
                if r.title() in v:
                    data[k][r] = "on"

        with open('/app/form_config.json', 'w', encoding="utf8") as f:
            json.dump(data, f, ensure_ascii=False)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(HOST, PORT)
        sock.connect((HOST, PORT))
        sock.sendall(b"Start scrapper.")
        sock.close()

    # If user has made config file, then use it to populate template.
    if os.path.isfile("/app/form_config.json"):
        with open('/app/form_config.json') as f:
            data = json.load(f)

    return render_template("index.html", items=data)
