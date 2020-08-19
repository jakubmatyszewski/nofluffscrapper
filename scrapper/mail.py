import datetime
import os
import ssl
import smtplib
import logging
from typing import List
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


def send_report(offerts: List) -> bool:
    _date = datetime.datetime.now()
    _email = os.environ.get("EMAIL")
    _password = os.environ.get("PASSWORD")
    try:
        len(_email)
    except TypeError:
        msg = "Credentials need to be specified to send email report."
        logging.warning(msg)
        return False
    port = 465

    # Create a secure SSL context
    context = ssl.create_default_context()

    message = f"""Subject: NoFluffScrapper - job report

    \nFound following offerts that may suit you:
    \n{''.join(offerts)}

    Report generated {_date.strftime("%d %B %Y")}."""

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(_email, _password)
        server.sendmail(_email, _email, message)
    logging.info(f"Report send to {_email}.")
    return True


def write_txt_report(offerts: List) -> bool:
    _date = datetime.datetime.now()
    file_name = f"report-{_date.strftime('%d%B%Y')}.txt"
    message = f"""Found following offerts that may suit you:
    \n{''.join(offerts)}\n"""

    with open(file_name, "w") as f:
        f.write(message)
    logging.info(f"Saved in {file_name}.")
    return True
