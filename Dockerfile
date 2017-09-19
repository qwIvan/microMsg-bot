FROM python:alpine
RUN apk add --update --no-cache gcc libxml2-dev libxslt-dev libc-dev
RUN pip install wxpy bs4 lxml flask gunicorn==18.0 flask_socketio eventlet js2py
ADD micro_msg_bot /micro_msg_bot
WORKDIR /data
EXPOSE 80
CMD PYTHONPATH=.. gunicorn --worker-class eventlet -w 1 micro_msg_bot.server:app -b 0.0.0.0:80 -t 300
