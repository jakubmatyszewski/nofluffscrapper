import os
import json
import argparse
import logging
from selenium import webdriver

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


def read_options(config_path="config.json"):
    with open(config_path) as f:
        config = json.load(f)
        _location = config['location']
        _category = config['category']
        _seniority = config['seniority']
        _stack = config['stack']
        _no_stack = config['no_stack']
        return _location, _category, _seniority, _stack, _no_stack


def run_scrapper():
    print("run_scrapper inside", flush=True)
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
