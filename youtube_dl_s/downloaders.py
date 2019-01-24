#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from time import time, mktime, strptime
import feedparser
import json
import logging
import youtube_dl

datetime_now = datetime.now()


class MyLogger(object):
    def debug(self, msg):
        logging.info(msg.strip())
        pass

    def warning(self, msg):
        logging.warning(msg.strip())
        pass

    def error(self, msg):
        logging.error(msg.strip())


def feedparser1(dl_opts):
    with open(dl_opts['json_file'], 'r', encoding='utf-8') as target:
        data = json.load(target)

    videos = []
    for name in data["outline"]:
        update = datetime.strptime(name["update"], "%Y-%m-%d %H:%M:%S")
        timeToLiveSeconds = timedelta(seconds=name["update_interval"])
        age = datetime_now - update
        if age <= timeToLiveSeconds:
            continue

        etag = name.get('etag')
        modified = name.get('modified')

        xmlUrl = name["xmlUrl"]
        logging.debug('[dl] ' + xmlUrl)

        feed = feedparser.parse(xmlUrl, etag=etag, modified=modified)

        if feed.get('etag'):
            name["etag"] = feed['etag']

        if feed.get('modified'):
            name["modified"] = feed['modified']

        try:
            name["status"] = feed['status']
        except KeyError:
            name["status"] = 0

        len_feed = range(0, len(feed['items']))
        for j in len_feed:
            timef = feed['items'][j]['published_parsed']
            dt = datetime.fromtimestamp(mktime(timef))
            logging.debug(f"[dl]   {str(dt)} {feed['items'][j]['link']}")
            if dt > update:
                videos.append(feed['items'][j]['link'])
                logging.debug('[dl]    ajout de la vidéo ci-dessus')

        name["update"] = datetime_now.strftime("%Y-%m-%d %H:%M:%S")

    with open(dl_opts['json_file'], 'w') as target:
        json.dump(data, target, indent=2)
    return videos


def YoutubeDLDownloader(ydl_opts, links=[]):
    len_links = len(links)
    if len_links == 0:
        logging.info('[dl] Sorry, no new video found')
        return

    logging.info(f"[dl] {str(len_links)} new videos found")
    ydl_opts['logger'] = MyLogger()
    errors = []
    for url in links:
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            errors += [url]
    return errors


if __name__ == "__main__":
    DATE = datetime.now().strftime('%Y-%m-%d')

    dl_opts = {
        'json_file': './data/feeds.json',
        'output': './data/watchlater/',
        'data': './data',
        'limit': 15
    }

    ydl_opts = {
        'mark_watched': True,
        'cookiefile': f"{dl_opts['data']}/cookies2.txt",
        'ignoreerrors': True,
        'writeinfojson': True,
        'outtmpl': f"{dl_opts['output']}{DATE}/%(id)s/%(id)s.%(ext)s",
        'download_archive': f"{dl_opts['data']}/archive-WL.txt",
        'is_live': False,
        'format': '[height<=?720][ext=mp4]/best'
    }

    # ~YoutubeDLDownloader(ydl_opts, feedparser1(dl_opts))
    print(feedparser1(dl_opts))
