#!/bin/env python3
from logger import logger
from flask import Flask
from bot import EmotionBot

app = Flask(__name__)


@app.route('/')
def login():
    def qr_callback(uuid, status, qrcode):
        logger.info('uuid=%s, status=%s', uuid, status)

    bot = EmotionBot(qr_callback=qr_callback, timeout_max=2)
    return '<img src=http://login.weixin.qq.com/qrcode/%s >' % bot.uuid


if __name__ == '__main__':
    app.run()
