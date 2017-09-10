import requests
import shelve
from bs4 import BeautifulSoup
from functools import lru_cache
from threading import Lock
from .logger import logger


@lru_cache()
def search(keyword):
    resp = requests.get('http://www.doutula.com/search', {'keyword': keyword})
    soup = BeautifulSoup(resp.text, 'lxml')
    result = ((i.get('data-original'), i.get('data-backup')[:-4]) for i in soup.select('img[data-original]') if i.get('class') != ['gif'])
    return [[url if not url.startswith('//') else 'http:' + url for url in imgs] for imgs in result]


def download_gif(f, *url):
    for u in url:
        resp = requests.get(u, allow_redirects=False)
        if resp.status_code == 200:
            f.write(resp.content)
            f.flush()
            return


keyword_dict_locks = Lock()
keyword_locks = {}
searched_lock = Lock()


def image_url(keyword):
    with keyword_dict_locks:
        kw_lock = keyword_locks.get(keyword, None)
        if not kw_lock:
            kw_lock = Lock()
            keyword_locks[keyword] = kw_lock

    with kw_lock:
        img = None
        with searched_lock:
            with shelve.open('searched') as searched:
                imgs = searched.get(keyword, None)
                if imgs:
                    img = imgs.pop(0)
                    imgs.append(img)
                    searched[keyword] = imgs
        if img:
            return img

        if not img:
            imgs = search(keyword)
            logger.info('New keyword "%s", %d result%s', keyword, len(imgs), 's' if len(imgs) > 1 else '')
            imgs = imgs[:10]
        if imgs:
            img = imgs.pop(0)
            imgs.append(img)
            with searched_lock:
                with shelve.open('searched') as searched:
                    searched[keyword] = imgs
            return img
