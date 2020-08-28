FROM python:3.8.5

ADD bot.py /

ADD reddit.py /

COPY requirements.txt .

RUN pip install -r requirements.txt

CMD [ "python", "./bot.py" ]
