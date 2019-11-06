#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from time import time, mktime, strptime
import datetime
import feedparser
import json
import logging
import youtube_dl

logger = logging.getLogger()
datetime_now = datetime.datetime.now()


class MyLogger(object):
    def debug(self, msg):
        logger.info(msg.strip())
        pass

    def warning(self, msg):
        logger.warning(msg.strip())
        pass

    def error(self, msg):
        logger.error(msg.strip())


def feedparser1(dl_opts):
    try:
        with open(dl_opts['json_file'], 'r', encoding='utf-8') as target:
            data = json.load(target)
    except FileNotFoundError as e:
        logger.warning(e)
        data = {}
        data["outline"] = []
        pass

    max_f = 0
    videos = []
    for name in data["outline"]:

        update = datetime.datetime.strptime(
            name["update"], "%Y-%m-%d %H:%M:%S")
        timeToLiveSeconds = datetime.timedelta(seconds=name["update_interval"])
        age = datetime_now - update
        if age <= timeToLiveSeconds:
            continue

        max_f += 1

        try:
            if not max_f < dl_opts['max_feed']:
                break
        except NameError:
            pass

        etag = name.get('etag')
        modified = name.get('modified')

        xmlUrl = name["xmlUrl"]
        logger.info(f'[feedparser]: {xmlUrl}')

        feed = feedparser.parse(xmlUrl, etag=etag, modified=modified)

        if feed.get('etag'):
            name["etag"] = feed['etag']

        if feed.get('modified'):
            name["modified"] = feed['modified']

        try:
            name["status"] = feed['status']
        except KeyError:
            name["status"] = 0

        addart = 0
        len_feed = range(0, len(feed['items']))
        for j in len_feed:
            timef = feed['items'][j]['published_parsed']
            timef = datetime.datetime.fromtimestamp(mktime(timef))
            logger.debug(
                f"[feedparser]:   {str(timef)} {feed['items'][j]['link']}")
            if timef > update:
                addart += 1
                art = dict()
                art['url'] = feed['items'][j]['link']
                art['title'] = feed['items'][j]['title']
                art['uploader'] = name['title']
                art['update'] = datetime_now.strftime("%Y-%m-%d %H:%M:%S")
                art['pass'] = 0
                videos.append(art)

        name["update"] = datetime_now.strftime("%Y-%m-%d %H:%M:%S")

        if addart >= 1:
            logger.info(f'[feedparser]:  => add {addart}')

    with open(dl_opts['json_file'], 'w') as target:
        json.dump(data, target, indent=2)
    return videos


def YoutubeDLDownloader(ydl_opts, links=[]):
    len_links = len(links)
    if len_links == 0:
        logger.info('[dl] Sorry, no new video found')
        return

    logger.info(f"[dl] {str(len_links)} new videos found")
    ydl_opts['logger'] = MyLogger()
    errors = []
    for url in links:
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception:
            errors += [url]
    return errors


if __name__ == "__main__":
    date = datetime.datetime.now().strftime('%Y-%m-%d')

    dl_opts = {
        'json_file': './data/feeds.json',
        'max_feed': 250
    }

    ydl_opts = {
        'mark_watched': True,
        'cookiefile': f"{dl_opts['data']}/cookies2.txt",
        'ignoreerrors': True,
        'writeinfojson': True,
        'outtmpl': f"{dl_opts['output']}{date}/%(id)s/%(id)s.%(ext)s",
        'download_archive': f"{dl_opts['data']}/archive-WL.txt",
        'is_live': False,
        'format': '[height<=?720][ext=mp4]/best'
    }

    # ~YoutubeDLDownloader(ydl_opts, feedparser1(dl_opts))
    print(feedparser1(dl_opts))
