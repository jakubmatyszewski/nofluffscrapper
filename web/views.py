import os
import json
import socket
import redis
from flask import Blueprint, render_template, request

bp = Blueprint('bp', __name__, template_folder='templates')
HOST = os.getenv('SEND_HOST')
PORT = int(os.getenv('SEND_PORT'))

redis_client = redis.Redis(host='redis')


def read_form_data():
    with open('/app/form_data.json') as f:
        data = json.load(f)
        return data


@bp.route('/', methods=['GET', 'POST'])
def home():
    data = read_form_data()

    if request.method == 'POST':
        results = {}
        form_output = request.form.keys()
        for r in form_output:
            for k, v in data.items():
                # v here is a dict, eg. {'remote': 'off'}
                # thus following line extracts true value
                v = [i.lower() for i in v.keys()]  # standarize casing
                r, k = (x.lower() for x in [r, k])  # standarize casing
                if r in v:
                    try:
                        results[k].append(r)
                    except KeyError:
                        results[k] = [r]

        # Save configuration to file
        with open('/app/form_config.json', 'w', encoding="utf8") as f:
            json.dump(data, f, ensure_ascii=False)

        # Save configuration to redis
        redis_data = json.dumps(results)
        redis_client.set("form_config", redis_data)

        # Call scrapper
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        sock.sendall(b"Start scrapper.")
        sock.close()

    # If user has made config file, then use it to populate template.
    if redis_client.get("form_config"):
        results = json.loads(redis_client.get("form_config"))
        for rv in results.values():
            for r in rv:
                for k, v in data.items():
                    if r.title() in v:
                        data[k][r.title()] = "on"

    return render_template("index.html", items=data)
