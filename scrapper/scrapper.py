import json
import argparse
import logging
import redis

from core import Scrapper
import mail

logging.getLogger().setLevel(logging.INFO)

#####
# Remove when Flask integration is done.
parser = argparse.ArgumentParser()
parser.add_argument('--no_email',
                    action='store_false',
                    help="Prevent sending report by email.\
                          Report will be saved in txt file.")
args = parser.parse_args()
EMAIL = args.no_email


redis_client = redis.Redis(host='redis',
                           charset="utf-8",
                           decode_responses=True)


def read_options():
    if redis_client.get("form_config"):
        config = json.loads(redis_client.get("form_config"))
        try:
            _location = config['Location']
        except KeyError:
            _location = []
        try:
            _category = config['Category']
        except KeyError:
            _category = []
        try:
            _seniority = config['Seniority']
        except KeyError:
            _seniority = []

    _no_stack, _stack = [], []
    for key in redis_client.scan_iter('stack:*'):
        key_formatted = ''.join(key.split(':')[1:])
        if (key_formatted.startswith('-')):
            skill = key_formatted[1:]
            _no_stack.append(skill)
        else:
            skill = key_formatted
            _stack.append(skill)
    return _location, _category, _seniority, _stack, _no_stack


def run_scrapper():
    logging.info('Running script..')
    web_scrap = Scrapper()
    location, category, seniority, stack, no_stack = read_options()
    web_scrap.get_filters_done(location, seniority, category)
    web_scrap.check_offers(stack, no_stack)
    if EMAIL is not False:
        mail.send_report(web_scrap.report)
    else:
        mail.write_txt_report(web_scrap.report)
    logging.info('Finished script..')
    web_scrap.close_browser()
    logging.info('Closed browser..')
