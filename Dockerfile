FROM python:alpine
RUN apk add --no-cache libxslt-dev
RUN apk add --no-cache --virtual .build-deps gcc libxml2-dev libc-dev \
  && pip install --no-cache-dir wxpy bs4 lxml flask gunicorn==18.0 flask_socketio eventlet js2py \
  && apk del .build-deps
#RUN apk add --no-cache --virtual .build-deps gcc libxml2-dev libxslt-dev libc-dev \
  #&& pip install --no-cache-dir wxpy bs4 lxml flask gunicorn==18.0 flask_socketio eventlet js2py
EXPOSE 80
ADD micro_msg_bot /micro_msg_bot
VOLUME /data
WORKDIR /data
CMD PYTHONPATH=/ gunicorn -k eventlet -w 1 micro_msg_bot.server:app -b 0.0.0.0:80 -t 300