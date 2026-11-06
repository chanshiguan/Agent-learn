"""只按人工审核的准确来源地址关联课程，不按整个域名猜教学覆盖。"""
import json
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


def normalize(url):
    parts = urlsplit(url)
    path = parts.path.rstrip('/')
    if parts.netloc == 'www.anthropic.com':
        path = path.replace('/research/', '/engineering/')
    return urlunsplit((parts.scheme,parts.netloc,path,parts.query,''))


READINGS = json.loads((Path(__file__).resolve().parents[1]/'reference/required-readings.json').read_text())


def destination(url):
    for row in READINGS:
        if normalize(row['source']) == normalize(url):
            return row['lesson'], row['title']+'：'+row['scope']
    return None
