FROM python:3.8-slim
COPY . /scrapper
WORKDIR /scrapper
RUN pip3 install -r requirements.txt
CMD ["python3", "receiver.py"]
