import os
import json
import argparse
import logging
from selenium import webdriver
from pyvirtualdisplay import Display

from app.core import Scrapper
import app.mail

logging.getLogger().setLevel(logging.INFO)
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


if __name__ == "__main__":
    try:
        display = os.environ["DISPLAY"]
    except KeyError:
        display_found = False
        display = Display(visible=0, size=(800, 600))
        display.start()
        logging.info('Initialized virtual display..')
    else:
        display_found = True

    web_scrap = Scrapper()
    location, category, seniority, stack, no_stack = read_options()
    web_scrap.get_filters_done(location, seniority, category)
    web_scrap.check_offers(stack, no_stack)
    if EMAIL is not False:
        app.mail.send_report(web_scrap.report)
    else:
        app.mail.write_txt_report(web_scrap.report)
    logging.info('Finished script..')
    web_scrap.close_browser()
    logging.info('Closed browser..')
    if display_found is False:
        display.stop()
        logging.info('Closed virtual display..')
