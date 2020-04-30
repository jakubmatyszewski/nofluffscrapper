import json
from selenium import webdriver

from app.core import Scrapper, close_browser
from app.mail import send_report


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
    web_scrap = Scrapper()
    web_scrap.set_language_to_english()
    location, category, seniority, stack, no_stack = read_options()
    web_scrap.get_filters_done(location, seniority, category)
    web_scrap.check_offers(stack, no_stack)
    send_report(web_scrap.report)
    close_browser()