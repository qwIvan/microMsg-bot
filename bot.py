import meme
import threading
from wxpy import *
from functools import lru_cache
from tempfile import NamedTemporaryFile


class EmotionBot(Bot):
    def __init__(self, *args, **kwargs):
        self.qr_lock = threading.Event()
        self.login_lock = threading.Event()
        _qr_callback = None
        if 'qr_callback' in kwargs:
            _qr_callback = kwargs['qr_callback']

        def qr_callback(uuid, status, qrcode):
            self.uuid = uuid
            if callable(_qr_callback):
                _qr_callback(uuid, status, qrcode)
            self.qr_lock.set()

        # kwargs.update(cache_path=True, qr_callback=qr_callback)
        kwargs.update(qr_callback=qr_callback)
        threading.Thread(target=self.login, args=args, kwargs=kwargs).start()
        self.qr_lock.wait()

    def login(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login_lock.set()
        self.ready()

    def ready(self):
        self.login_lock.wait()

        @lru_cache()
        def gif_media_id(*url):
            tmp = NamedTemporaryFile()
            try:
                meme.download_gif(tmp, *url)
                media_id = self.upload_file(tmp.name)
            finally:
                tmp.close()
            return media_id

        searched = {}

        @self.register(msg_types=TEXT, except_self=False)
        def reply(msg):
            if msg.text[-4:] in ('.gif', '.jpg'):
                keyword = msg.text[:-4]
                imgs = keyword in searched and searched[keyword]
                if not imgs:
                    imgs = meme.search(keyword)
                    searched[keyword] = imgs
                if imgs:
                    media_id = gif_media_id(*imgs.pop(0))
                    msg.reply_image('.gif', media_id=media_id)

                    # @self.register(msg_types=FRIENDS)
                    # def gdg_offical_group(msg):
                    #     msg.card.accept()

    def print_cookies(self):
        for n, v in self.core.s.cookies.items():
            print("document.cookie='{}={};domain=.qq.com;expires=Fri, 31 Dec 9999 23:59:59 GMT'".format(n, v))

            # import sys
            # if len(sys.argv) > 1 and sys.argv[1] == '-c':
            #     print_cookies()
