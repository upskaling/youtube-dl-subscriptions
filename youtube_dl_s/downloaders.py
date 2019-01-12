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
    max_videos = True
    for name in data["outline"]:
        if max_videos:  # arrêter
            update = datetime.strptime(name["update"], "%Y-%m-%d %H:%M:%S")
            #
            update_interval = timedelta(seconds=-name["update_interval"])
            update_interval = update_interval + datetime_now

            if update_interval > update:
                xmlUrl = name["xmlUrl"]
                logging.debug('[dl] ' + xmlUrl)

                feed = feedparser.parse(xmlUrl)
                len_feed = len(feed['items'])

                for j in range(0, len_feed):
                    if max_videos:  # arrêter
                        timef = feed['items'][j]['published_parsed']
                        dt = datetime.fromtimestamp(mktime(timef))
                        logging.debug(f"[dl]   {str(dt)} {feed['items'][j]['link']}")
                        if dt > update:
                            videos.append(feed['items'][j]['link'])
                            logging.debug(
                                '[dl]    ajout de la vidéo ci-dessus')
                            if dl_opts['limit']:
                                if len(videos) >= dl_opts['limit']:
                                    max_videos = False
                if max_videos:
                    name["update"] = datetime_now.strftime("%Y-%m-%d %H:%M:%S")

    with open(dl_opts['json_file'], 'w') as target:
        json.dump(data, target, indent=2)
    return videos


def YoutubeDLDownloader(ydl_opts, url=[]):
    len_videos = len(url)
    if len_videos == 0:
        logging.info('[dl] Sorry, no new video found')
    else:
        logging.info('[dl] ' + str(len_videos) + ' new videos found')
        ydl_opts['logger'] = MyLogger()
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)


def YoutubeDLWatchlater(ydl_opts):
    watchlater = ['https://www.youtube.com/playlist?list=WL']
    logging.info("[dl] watchlater")
    ydl_opts['logger'] = MyLogger()
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(watchlater)


if __name__ == "__main__":
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

    YoutubeDLDownloader(ydl_opts, feedparser1(dl_opts))
