#!/bin/env python3
import shelve
import secrets
import os
from logger import logger
from flask import Flask, request, session
from bot import EmotionBot, SyncEmotionBot
from flask_socketio import SocketIO, emit, join_room
from threading import Lock

app = Flask(__name__)
app.secret_key = 'test'
socketio = SocketIO(app)


@app.route('/')
def login():
    if 'sessionID' not in session:
        session['sessionID'] = str(secrets.randbits(256))
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
bot_status_lock = Lock()


@socketio.on('login')
def login():

    def success_ack(bot, sessionID, nickname):
        socketio.emit('success', (dict(bot.core.s.cookies.items()), bot.core.loginInfo['url'], nickname), room=sessionID)

    def background_thread(sid, sessionID):

        def qr_callback(uuid, status, qrcode):
            logger.info('%s %s', uuid, status)
            if status != '408':
                socketio.emit('qr', (uuid, status), room=sessionID)

        def logout_callback():
            with bot_status_lock:
                with shelve.open('bot_status') as bot_status:
                    bot_status[sessionID] = False
            if sessionID in bots:
                logger.info('%s logged out!', bots[sessionID].self.name)
                del bots[sessionID]
            os.remove(sessionID)
            socketio.emit('logout', room=sessionID)

        def login_callback():
            if hasattr(bots.get(sessionID, None), 'logout'):
                bots[sessionID].logout()

        try:
            bot = EmotionBot(qr_callback=qr_callback, cache_path=sessionID, logout_callback=logout_callback, login_callback=login_callback)
            # socketio.server.enter_room(room=cache_path, sid=sid)
            bots[sessionID] = bot
            with bot_status_lock:
                with shelve.open('bot_status') as bot_status:
                    bot_status[sessionID] = bot.alive
            logger.info('%s logged in, cache at %s', bot.self.name, sessionID)
            success_ack(bot, sessionID, bot.self.name)
        except EmotionBot.TimeoutException as e:
            logger.warning('uuid=%s, status=%s, timeout', e.uuid, e.status)
            socketio.emit('qr', (e.uuid, 'timeout'), room=sessionID)

    if 'sessionID' not in session:
        return
    join_room(room=session['sessionID'], sid=request.sid)
    bot = bots.get(session['sessionID'], None)
    if hasattr(bot, 'alive') and bot.alive and hasattr(bot, 'self') and hasattr(bot.self, 'name') and bot.self.name:
        success_ack(bot, request.sid, bot.self.name)
    else:
        socketio.start_background_task(background_thread, sid=request.sid, sessionID=session['sessionID'])


if __name__ == '__main__':
    socketio.run(app)
