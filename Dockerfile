FROM python:alpine
RUN apk update && apk add gcc libxml2-dev libxslt-dev libc-dev
RUN pip install wxpy bs4 lxml flask gunicorn flask_socketio
ADD . /code
WORKDIR /code
EXPOSE 8000
CMD gunicorn server:app -b 0.0.0.0
