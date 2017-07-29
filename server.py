#!/bin/env python3
import shelve
import secrets
import os
from logger import logger
from flask import Flask, request, session
from bot import EmotionBot, SyncEmotionBot
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = 'test'
socketio = SocketIO(app)


@app.route('/')
def login():
    if 'cache_path' not in session:
        session['cache_path'] = str(secrets.randbits(256))
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

bots = {}


@socketio.on('login')
def login():

    def success_ack(bot, sid, nickname):
        socketio.emit('success', (dict(bot.core.s.cookies.items()), bot.core.loginInfo['url'], nickname), room=sid)

    def background_thread(sid, cache_path):

        def qr_callback(uuid, status, qrcode):
            logger.info('%s %s', uuid, status)
            if status != '408':
                socketio.emit('qr', (uuid, status), room=sid)

        def logout_callback():
            with shelve.open('bot_status') as bot_status:
                bot_status[cache_path] = False
            if cache_path in bots:
                logger.info('%s logged out!', bots[cache_path].self.name)
                del bots[cache_path]
            os.remove(cache_path)
            socketio.emit('logout', room=sid)

        def login_callback():
            if hasattr(bots.get(cache_path, None), 'logout'):
                bots[cache_path].logout()

        try:
            bot = EmotionBot(qr_callback=qr_callback, cache_path=cache_path, logout_callback=logout_callback, login_callback=login_callback)
            bots[cache_path] = bot
            with shelve.open('bot_status') as bot_status:
                bot_status[cache_path] = bot.alive
            logger.info('%s logged in, cache at %s', bot.self.name, cache_path)
            success_ack(bot, sid, bot.self.name)
        except EmotionBot.TimeoutException as e:
            logger.warning('uuid=%s, status=%s, timeout', e.uuid, e.status)
            socketio.emit('qr', (e.uuid, 'timeout'), room=sid)

    if 'cache_path' not in session:
        return
    bot = bots.get(session['cache_path'], None)
    if hasattr(bot, 'alive') and bot.alive and hasattr(bot, 'self') and hasattr(bot.self, 'name') and bot.self.name:
        success_ack(bot, request.sid, bot.self.name)
    else:
        socketio.start_background_task(background_thread, sid=request.sid, cache_path=session['cache_path'])


if __name__ == '__main__':
    socketio.run(app)
