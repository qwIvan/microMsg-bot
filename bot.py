import meme
from wxpy import *
from functools import lru_cache
from tempfile import NamedTemporaryFile
bot = Bot(cache_path=True, console_qr=True)
# bot = Bot(console_qr=True)


@lru_cache()
def gif_media_id(*url):
    tmp = NamedTemporaryFile()
    try:
        meme.download_gif(tmp, *url)
        media_id = bot.upload_file(tmp.name)
    finally:
        tmp.close()
    return media_id


searched = {}


@bot.register(msg_types=TEXT, except_self=False)
def accept(msg):
    if msg.text[-4:] in ('.gif', '.jpg'):
        keyword = msg.text[:-4]
        imgs = keyword in searched and searched[keyword]
        if not imgs:
            imgs = meme.search(keyword)
            searched[keyword] = imgs
        if imgs:
            media_id = gif_media_id(*imgs.pop(0))
            msg.reply_image('.gif', media_id=media_id)


@bot.register(msg_types=FRIENDS)
def gdg_offical_group(msg):
    msg.card.accept()


def print_cookies(bot=bot):
    for n, v in bot.core.s.cookies.items():
        print("document.cookie='{}={};domain=.qq.com;expires=Fri, 31 Dec 9999 23:59:59 GMT'".format(n, v))
import sys
if len(sys.argv) > 1 and sys.argv[1] == '-c':
    print_cookies()

bot.join()
