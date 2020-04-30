import datetime
import os
import ssl
import smtplib
from typing import List
from dotenv import load_dotenv
load_dotenv()


def send_report(offerts: List) -> bool:
    _date = datetime.datetime.now()
    _email = os.environ.get("EMAIL")
    password = os.environ.get("PASSWORD")
    port = 465

    # Create a secure SSL context
    context = ssl.create_default_context()

    message = f"""Subject: NoFluffScrapper - job report
    
    \nFound following offerts that may suit you:
    \n{''.join(offerts)}
    
    Report generated {_date.strftime("%d %B %Y")}."""

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(_email, password)
        server.sendmail(_email, _email, message)
    return True


if __name__ == "__main__":
    send_report(['text', 'test', 'please'])