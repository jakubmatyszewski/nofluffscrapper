FROM python:3.8-slim

ENV APP_HOME /usr/src/app
WORKDIR /$APP_HOME

COPY . $APP_HOME/

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "scrapper.py"]
