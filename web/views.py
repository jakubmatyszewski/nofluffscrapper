import os
import json
import socket
import random
import redis
from flask import Blueprint, render_template, request, jsonify, app

bp = Blueprint('bp', __name__, template_folder='templates')
HOST = os.getenv('SEND_HOST')
PORT = int(os.getenv('SEND_PORT'))

redis_client = redis.Redis(host='redis',
                           charset="utf-8",
                           decode_responses=True)

app.current_pag = []


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
                v = [i for i in v.keys()]
                if r in v:
                    try:
                        results[k].append(r)
                    except KeyError:
                        results[k] = [r]

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
                    if r in v:
                        data[k][r] = "on"

    stack = {}
    for key in redis_client.scan_iter('stack:*'):
        if (stack_key := redis_client.get(key)):
            stack[''.join(key.split(':')[1:])] = stack_key

    return render_template("index.html",
                           form_items=data,
                           stack_items=stack,
                           )


@bp.route('/config_stack')
def config_stack():
    try:
        stack = request.args.get('stack', 0, type=str).lower()
        if len(stack) == 0:
            pass
        elif stack.startswith('-'):
            redis_client.set(f'stack:{stack.strip()}', 0)
            return jsonify(result=stack)
        else:
            redis_client.set(f'stack:{stack.strip()}', 1)
            return jsonify(result=stack)
    except Exception as e:
        return str(e)


@bp.route('/add_suggested_skill')
def add_suggested_skill():
    try:
        skill = request.args.get('skill', 0, type=str).lower()
        redis_client.set(f'stack:{skill.strip()}', 1)
        redis_client.delete(f'skillproposal:{skill}')
        app.current_pag.remove(skill)
        return jsonify(result=app.current_pag)
    except Exception as e:
        return str(e)


@bp.route('/remove_skill')
def remove_skill():
    try:
        skill = request.args.get('skill', 0, type=str)
        redis_client.delete(f'stack:{skill}')
        return jsonify(removed=True)
    except Exception as e:
        return str(e)


@bp.route('/paginate_suggestions')
def paginate_suggestions():
    all_skills = [redis_client.get(s)
                  for s in redis_client.scan_iter('skillproposal:*')]
    available_suggestions = all_skills

    if len(all_skills) <= 5:
        pagination = len(all_skills)
    else:
        pagination = 5

    if len(app.current_pag) == 0:
        app.current_pag = random.sample(all_skills, pagination)
        return jsonify(result=app.current_pag)
    else:
        for skill in app.current_pag:
            if skill in all_skills:
                available_suggestions.remove(skill)

        if len(app.current_pag) < pagination:
            try:
                # Populate displayed suggestions with new one
                new_suggestion = random.sample(available_suggestions, 1)
                app.current_pag.append(new_suggestion[0])
            except ValueError:  # No more suggestions
                pass
        else:
            app.current_pag = random.sample(all_skills, pagination)

        return jsonify(result=app.current_pag)
