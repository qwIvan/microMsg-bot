FROM python:alpine
RUN apk update && apk add gcc libxml2-dev libxslt-dev libc-dev
RUN pip install wxpy bs4 lxml flask gunicorn==18.0 flask_socketio eventlet
ADD . /code
WORKDIR /code
EXPOSE 80
CMD gunicorn --worker-class eventlet -w 1 server:app -b 0.0.0.0:80
