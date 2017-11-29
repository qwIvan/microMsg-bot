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
    if msg.lower().strip()[-4:] in ('.gif', '.jpg', '.png'):
        keyword = msg.strip()[:-4].strip()
        return keyword, 1
    else:
        groups = re.findall('(.*)\.(jpg|gif|png)\s*(x|×|X|\*)\s*(\d+)\s*$', msg, re.I)
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
    groups = re.findall('(.*)\s*(x|×|X|\*)\s*(\d+)\s*$', keyword)
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
        logger.info('%s searched keyword "%s"', bot.self.name, keyword)
        img = meme.image_url(keyword)
        if img:
            media_id = gif_media_id(*img)
            logger.info('image: "%s", media_id: %s', img, media_id)
            return media_id

    print('okok')
    fxh = None
    hksx = None
    for g in bot.groups(update=False):
        if g.self.display_name == '分享会':
            fxh = g
            print(g)
        elif g.self.display_name == '香港实习':
            hksx = g
            print(g)
    #if not fxh or not hksx:
    #    print('groups not found')
    #    sys.exit(333)

    @bot.register(msg_types=TEXT)
    def handle_text(msg: Message):
        print(msg)
        if isinstance(msg.sender, Group):
            return
        if msg.text.strip() == '分享会':
            try:
                fxh.add_members(msg.sender, use_invitation=True)
            except:
                bot.add_friend(msg.sender)
                fxh.add_members(msg.sender, use_invitation=True)
        elif msg.text.strip() == '香港实习':
            try:
                hksx.add_members(msg.sender, use_invitation=True)
            except:
                bot.add_friend(msg.sender)
                hksx.add_members(msg.sender, use_invitation=True)

    # fds = []

    @bot.register(msg_types=FRIENDS)
    def accept_friends(msg: Message):
        print(msg)
        text = msg.text.strip()
        print(text)
        new_friend = msg.card.accept()
        print(new_friend)
        fxh.add_members(new_friend, use_invitation=True)
        print('invited')
        new_friend.send('''哇，终于等到你！  [太阳]回复关键词“分享会”，即可直接获得进群链接哟~  未来还会有更多牛逼的师兄师姐将以线上分享的方式在微信群开讲！满满的干货，让我们一起加油成长起来[转圈]''')
        # fds.append(new_friend)

    @bot.register(msg_types=NOTE)
    def accept_friends(msg: Message):
        print(msg)
        print(msg.text)
        if '刚刚把你添加到通讯录' in msg.text or '请先发送朋友验证请求' in msg.text:
            bot.add_friend(msg.sender)
            print('add')
        fxh.add_members(msg.sender, use_invitation=True)
        msg.sender.send('''哇，终于等到你！  [太阳]回复关键词“分享会”，即可直接获得进群链接哟~  未来还会有更多牛逼的师兄师姐将以线上分享的方式在微信群开讲！满满的干货，让我们一起加油成长起来[转圈]''')

