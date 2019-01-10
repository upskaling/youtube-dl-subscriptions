#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from time import time, mktime, strptime
import feedparser
import json
import logging
import youtube_dl

datetime_now = datetime.now()
DATE = datetime.now().strftime('%Y-%m-%d')


def feedparser1(dl_opts):
    with open(dl_opts['json_file'], 'r', encoding='utf-8') as target:
        data = json.load(target)

    # ~print(sorted(data["outline"]))
    videos = []
    max_videos = False
    for name in data["outline"]:
        update = name["update"]
        update = datetime.strptime(update, "%Y-%m-%d %H:%M:%S")
        #
        update_interval = name["update_interval"]
        update_interval = timedelta(seconds=-update_interval)
        update_interval = update_interval + datetime_now

        if max_videos is False:  # arrêter
            if update_interval > update:
                xmlUrl = name["xmlUrl"]
                logging.debug('[dl] ' + xmlUrl)

                feed = feedparser.parse(xmlUrl)
                len_feed = len(feed['items'])

                for j in range(0, len_feed):
                    timef = feed['items'][j]['published_parsed']
                    dt = datetime.fromtimestamp(mktime(timef))
                    logging.debug(
                        f"[dl]   {str(dt)} {feed['items'][j]['link']}")
                    if dt > update:
                        if max_videos is False:  # arrêter
                            videos.append(feed['items'][j]['link'])
                            logging.debug(
                                '[dl]    ajout de la vidéo ci-dessus')
                            if len(videos) >= 15:
                                max_videos = True
                                # print(max_videos)
                # update time
                with open(dl_opts['json_file'], 'w') as target:
                    name["update"] = datetime_now.strftime("%Y-%m-%d %H:%M:%S")
                    json.dump(data, target, indent=4)
    return videos


def YoutubeDLDownloader(dl_opts, url=[]):

    class MyLogger(object):
        def debug(self, msg):
            logging.info(msg.strip())
            pass

        def warning(self, msg):
            logging.warning(msg.strip())
            pass

        def error(self, msg):
            logging.error(msg.strip())

    ydl_opts = {
        'mark_watched': True,
        'cookiefile': f"{dl_opts['data']}/cookies2.txt",
        'ignoreerrors': True,
        'writeinfojson': True,
        'outtmpl': f"{dl_opts['output']}{DATE}/%(id)s/%(id)s.%(ext)s",
        'download_archive': f"{dl_opts['data']}/archive-WL.txt",
        'is_live': False,
        'format': dl_opts['format'],
        'logger': MyLogger(),
    }

    len_videos = len(url)
    if len_videos == 0:
        logging.info('[dl] Sorry, no new video found')
    else:
        logging.info('[dl] ' + str(len_videos) + ' new videos found')
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)

    if dl_opts['watchlater'] is True:
        watchlater = ['https://www.youtube.com/playlist?list=WL']
        logging.info("[dl] watchlater")
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download(watchlater)


if __name__ == "__main__":
    dl_opts = {
        'json_file': './data/feeds.json',
        'output': './data/watchlater',
        'data': './data',
        'format': '[height<=?720][ext=mp4]/best',
    }

    YoutubeDLDownloader(dl_opts, feedparser1(dl_opts))
