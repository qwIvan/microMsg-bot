#!/usr/bin/env python3
import re
from wxpy import *
from functools import lru_cache
from tempfile import NamedTemporaryFile
from concurrent.futures import ThreadPoolExecutor
from . import meme
from .logger import logger

pool = ThreadPoolExecutor(100)


class BotSetting:
    suffix_reply = True
    at_reply = False
    # TODO blacklist or white list


def reg_event(bot):
    @lru_cache()
    def gif_media_id(*url):
        tmp = NamedTemporaryFile()
        try:
            logger.info('Downloading image, URLs: %s', url)
            meme.download_gif(tmp, *url)
            logger.info('Uploading image, URLs: %s', url)
            media_id = bot.upload_file(tmp.name)
        finally:
            tmp.close()
        return media_id

    def media_id_by(keyword):
        logger.info('keyword "%s"', keyword)
        img = meme.image_url(keyword)
        if img:
            media_id = gif_media_id(*img)
            logger.info('image: "%s", media_id: %s', img, media_id)
            return media_id

    @bot.register(msg_types=TEXT, except_self=False)
    def reply(msg: Message):
        if bot.setting.suffix_reply:
            if msg.text[-4:] in ('.gif', '.jpg'):
                keyword = msg.text[:-4]
                media_id = media_id_by(keyword)
                msg.reply_image('.gif', media_id=media_id)
                return
            else:
                groups = re.findall('(.*)\.(jpg|gif)\s*(x|×|X)\s*(\d+)$', msg.text)
                if groups and groups[0][-1].isdigit():
                    group = groups[0]
                    keyword = group[0]
                    times = int(group[-1])
                    if times > 5:
                        times = 5
                    for media_id in pool.map(media_id_by, [keyword] * times, chunksize=times):
                        msg.reply_image('.gif', media_id=media_id)
                    return
        if bot.setting.at_reply and msg.is_at and isinstance(msg.sender, Group):
            keyword = re.sub('@%s' % msg.sender.self.name, '', msg.text, 1).strip()
            groups = re.findall('(.*)\s*(x|×|X)(\d+)$', keyword)
            if groups and groups[0][-1].isdigit():
                group = groups[0]
                keyword = group[0]
                times = int(group[-1])
                if times > 5:
                    times = 5
            else:
                times = 1
            for media_id in pool.map(media_id_by, [keyword] * times, chunksize=times):
                msg.reply_image('.gif', media_id=media_id)
            return


if __name__ == '__main__':
    bot = Bot(console_qr=True)
    reg_event(bot)
    bot.join()
