#!/usr/bin/env python3
import re
import functools
from wxpy import *
from tempfile import NamedTemporaryFile
from concurrent.futures import ThreadPoolExecutor
from . import meme
from .logger import logger

pool = ThreadPoolExecutor(100)


class BotSetting:
    suffix_reply = True
    at_reply = False
    # TODO blacklist or white list


def keyword_by_suffix(msg: str):
    prefix, _, suffix = msg.lower().strip().rpartition('.')
    if suffix.strip() in ('gif', 'jpg', 'png', 'webp'):
        return prefix.strip(), 1
    else:
        groups = re.findall('(.*)\.(jpg|gif|png|webp)\s*(x|×|X|\*)\s*(\d+)\s*$', msg, re.I)
        if groups and groups[0][-1].isdigit():
            group = groups[0]
            keyword = group[0].strip()
            times = int(group[-1])
            if times > 5:
                times = 5
            return keyword, times
        else:
            return None, 0


def keyword_by_at(msg: str, name):
    keyword = re.sub('@%s' % name, '', msg, 1).strip()
    groups = re.findall('(.*)\s*(x|×|X|✖️|\*)\s*(\d+)\s*$', keyword)
    if groups and groups[0][-1].isdigit():
        group = groups[0]
        keyword = group[0].strip()
        times = int(group[-1])
        if times > 5:
            times = 5
    else:
        times = 1
    return keyword, times


@functools.lru_cache()
def _gif_media_id(*url, bot):
    tmp = NamedTemporaryFile()
    try:
        logger.info('Downloading image, URLs: %s', url)
        meme.download_gif(tmp, *url)
        logger.info('Uploading image, URLs: %s', url)
        media_id = bot.upload_file(tmp.name)
    finally:
        tmp.close()
    return media_id


def reg_event(bot):
    gif_media_id = functools.partial(_gif_media_id, bot=bot)

    def media_id_by(keyword):
        img = meme.image_url(keyword)
        if img:
            media_id = gif_media_id(*img)
            logger.info('image: "%s", media_id: %s', img, media_id)
            return media_id

    @bot.register(msg_types=TEXT, except_self=False)
    def reply(msg: Message):
        keyword, times = None, 0
        if bot.setting.suffix_reply:
            keyword, times = keyword_by_suffix(msg.text)
        if not keyword and bot.setting.at_reply and msg.is_at and isinstance(msg.sender, Group):
            keyword, times = keyword_by_at(msg.text, msg.sender.self.name)

        if keyword:
            logger.info('%s searched keyword "%s" x %d', bot.self.name, keyword, times)
            for media_id in pool.map(media_id_by, [keyword] * times, chunksize=times):
                msg.reply_image('.gif', media_id=media_id)
