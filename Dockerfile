FROM python:3.6-alpine
RUN apk add --no-cache libxslt-dev
RUN apk add --no-cache --virtual .build-deps gcc libxml2-dev libc-dev \
  && pip install --no-cache-dir wxpy bs4 lxml flask gunicorn==18.0 flask_socketio eventlet js2py \
  && apk del .build-deps
EXPOSE 80
ADD micro_msg_bot /micro_msg_bot
RUN pip install --no-cache-dir pytest \
  && pytest /micro_msg_bot/testing.py
VOLUME /data
WORKDIR /data
CMD PYTHONPATH=/ gunicorn -k eventlet -w 1 micro_msg_bot.server:app -b 0.0.0.0:80 -t 300
