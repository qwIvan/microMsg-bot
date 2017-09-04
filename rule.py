import meme
import re
from wxpy import *
from logger import logger
from functools import lru_cache
from tempfile import NamedTemporaryFile


def reg_event(bot):
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
        if msg.sender == bot.self and '开启自动斗图' in msg.text:
            bot.at_reply_groups.add(msg.receiver)
            logger.info('群聊<%s>已开启自动斗图' % msg.receiver.name)
            return '已开启，@我发送文字可以自动斗图'
        elif msg.sender == bot.self and '关闭自动斗图' in msg.text and msg.receiver in bot.at_reply_groups:
            bot.at_reply_groups.remove(msg.receiver)
            logger.info('群聊<%s>已关闭自动斗图' % msg.receiver.name)
            return '已关闭'

        keyword = None
        if msg.text[-4:] in ('.gif', '.jpg'):
            keyword = msg.text[:-4]
        elif msg.is_at and msg.sender in bot.at_reply_groups:
            keyword = re.sub('@\S+', '', msg.text)
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
