#!/bin/env python3
from logger import logger
from flask import Flask
from bot import EmotionBot, SyncEmotionBot
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/')
def login():
    def qr_callback(uuid, status, qrcode):
        logger.info('uuid=%s, status=%s', uuid, status)

    try:
        bot = SyncEmotionBot(qr_callback=qr_callback, timeout_max=15)
    except EmotionBot.TimeoutException as e:
        logger.warning('uuid=%s, status=%s, timeout', e.uuid, e.status)
    return '<img src=http://login.weixin.qq.com/qrcode/%s >' % bot.uuid


@socketio.on('login')
def login(msg):
    logger.info(msg)

    def qr_callback(uuid, status, qrcode):
        logger.info('%s %s', uuid, status)
        if status == '0':
            emit('qr', uuid)

    try:
        bot = EmotionBot(qr_callback=qr_callback)
    except EmotionBot.TimeoutException as e:
        logger.warning('uuid=%s, status=%s, timeout', e.uuid, e.status)


if __name__ == '__main__':
    # app.run()
    socketio.run(app)
