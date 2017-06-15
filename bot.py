import meme
from wxpy import *
from functools import lru_cache
bot = Bot(cache_path=True, console_qr=True)
# bot = Bot(console_qr=True)


@lru_cache()
def gif_media_id(*url):
    try:
        gif = meme.download_gif(*url)
        return bot.upload_file(gif.name)
    finally:
        gif.close()


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


bot.join()
