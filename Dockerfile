FROM python:3.8-alpine

RUN apk update \
    && apk add --no-cache tk-dev python3-tkinter

WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

VOLUME /usr/src/app/.env /usr/src/app/santa.db /usr/src/app/logs/

CMD ["python", "bot.py"]
