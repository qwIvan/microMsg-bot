#!/usr/bin/env python3
import re
from wxpy import *
from functools import lru_cache
from tempfile import NamedTemporaryFile
from . import meme
from .logger import logger


def reg_event(bot):
    # bot.at_reply_groups = set()  # TODO
    # bot.at_reply_blacklist = True  # blacklist (default) or white list
    bot.suffix_reply_enable = True
    bot.at_reply_enable = False

    @lru_cache()
    def gif_media_id(*url):
        tmp = NamedTemporaryFile()
        try:
            meme.download_gif(tmp, *url)
            media_id = bot.upload_file(tmp.name)
        finally:
            tmp.close()
        return media_id

    @bot.register(msg_types=TEXT, except_self=False)
    def reply(msg):
        keyword = None
        if bot.suffix_reply_enable and msg.text[-4:] in ('.gif', '.jpg'):
            keyword = msg.text[:-4]
        elif bot.at_reply_enable and msg.is_at and isinstance(msg.sender, Group):
            keyword = re.sub('@%s' % msg.sender.self.display_name, '', msg.text, 1).strip()
            print(msg.sender.self.display_name)
        if keyword:
            img = meme.image_url(keyword)
            if img:
                logger.info('Uploading image, URLs: %s', img)
                media_id = gif_media_id(*img)
                logger.info('Received keyword "%s", reply image with media_id %s', keyword, media_id)
                msg.reply_image('.gif', media_id=media_id)


if __name__ == '__main__':
    bot = Bot(console_qr=True)
    reg_event(bot)
    bot.join()
