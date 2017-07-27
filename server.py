#!/bin/env python3
from logger import logger
from flask import Flask, request, url_for
from bot import EmotionBot, SyncEmotionBot
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/')
def login():
    return app.send_static_file('index.html')
#     def qr_callback(uuid, status, qrcode):
#         logger.info('uuid=%s, status=%s', uuid, status)
#
#     def login_calback():
#         bot.print_cookies()
#
#     try:
#         bot = SyncEmotionBot(qr_callback=qr_callback, timeout_max=15, login_callback=login_calback)
#     except EmotionBot.TimeoutException as e:
#         logger.warning('uuid=%s, status=%s, timeout', e.uuid, e.status)
#     return '<img src=http://login.weixin.qq.com/qrcode/%s >' % bot.uuid


@socketio.on('login')
def login():

    def background_thread(sid):

        def qr_callback(uuid, status, qrcode):
            logger.info('%s %s', uuid, status)
            if status != '408':
                socketio.emit('qr', (uuid, status), room=sid)

        try:
            bot = EmotionBot(qr_callback=qr_callback, cache_path=sid)
            bot.print_cookies()
        except EmotionBot.TimeoutException as e:
            logger.warning('uuid=%s, status=%s, timeout', e.uuid, e.status)
            socketio.emit('qr', (e.uuid, 'timeout'), room=sid)

    socketio.start_background_task(background_thread, sid=request.sid)


if __name__ == '__main__':
    socketio.run(app)
