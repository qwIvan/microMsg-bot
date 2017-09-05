import threading
from wxpy import *
from .rule import reg_event
from .logger import logger


class EmotionBot(Bot):
    class TimeoutException(Exception):
        def __init__(self, uuid, status):
            self.uuid = uuid
            self.status = status

    def __init__(self, name=None, need_login=True, timeout_max=15, qr_callback=None, *args, **kwargs):
        self.name = name
        self.timeout_count = 0  # QR code timeout count
        self.at_reply_groups = set()  # auto reply is_at msg from these groups

        if need_login:
            self.login(timeout_max=timeout_max, qr_callback=qr_callback, *args, **kwargs)

    def login(self, timeout_max=15, qr_callback=None, *args, **kwargs):
        def _qr_callback(uuid, status, qrcode):
            if status == '408':
                self.timeout_count += 1
                if self.timeout_count > timeout_max:
                    raise self.TimeoutException(uuid, status)
            elif status == '400':  # exit thread when time out at QR code waiting for scan
                raise self.TimeoutException(uuid, status)
            if callable(qr_callback):
                qr_callback(uuid, status, qrcode)

        super().__init__(qr_callback=_qr_callback, *args, **kwargs)
        reg_event(self)


class SyncEmotionBot(EmotionBot):
    def __init__(self, need_login=True, *args, **kwargs):
        super().__init__(need_login=False, *args, **kwargs)
        self.uuid_lock = threading.Event()
        self.login_lock = threading.Event()
        self.timeout_count = 0  # QR code timeout count
        self.thread = None

        if need_login:
            self.login(*args, **kwargs)

    def login(self, qr_callback=None, *args, **kwargs):
        def _qr_callback(uuid, status, qrcode):
            if status == '0':
                self.uuid = uuid
                self.uuid_lock.set()
            if callable(qr_callback):
                qr_callback(uuid, status, qrcode)

        kwargs.update(qr_callback=_qr_callback)
        self.thread = threading.Thread(target=self._login_thread, args=args, kwargs=kwargs)
        self.thread.start()
        self.uuid_lock.wait()  # lock release when QR code uuid got
        return self.uuid

    def _login_thread(self, *args, **kwargs):
        try:
            super().login(*args, **kwargs)
        except self.TimeoutException as e:
            logger.warning('uuid=%s, status=%s, timeout', e.uuid, e.status)
            return
        self.login_lock.set()

    def is_logged(self, timeout=None):
        return self.login_lock.wait(timeout)
