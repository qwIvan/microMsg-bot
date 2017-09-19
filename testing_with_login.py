from .testing import *
from .bot import EmotionBot

bot = EmotionBot(console_qr=True, cache_path='wxpy_bot.pkl')


def test_get_media_id():
    from .rule import _gif_media_id
    return _gif_media_id(*test_meme_url(), bot=bot)


def test_send():
    bot.file_helper.send_image('.gif', media_id=test_get_media_id())
