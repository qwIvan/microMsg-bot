import requests
from tempfile import NamedTemporaryFile
from bs4 import BeautifulSoup
from functools import lru_cache


@lru_cache()
def search(keyword):
    resp = requests.get('https://www.doutula.com/search', {'keyword': keyword})
    soup = BeautifulSoup(resp.text, 'lxml')
    return [('http:' + i.get('data-original'), 'http:' + i.get('data-backup')[:-4]) for i in soup.select('.select-container img') if i.get('class') != ['gif']]


def download_gif(*url):
    for u in url:
        resp = requests.get(u, allow_redirects=False)
        if resp.status_code == 200:
            tmp = NamedTemporaryFile()
            tmp.write(resp.content)
            tmp.flush()
            return tmp
