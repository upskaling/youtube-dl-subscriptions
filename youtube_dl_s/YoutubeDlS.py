#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from youtube_dl_s import ls
import argparse
import datetime
import json
import logging
import pathlib
import socket

now = datetime.datetime.now()

DATE = datetime.datetime.now().strftime('%Y-%m-%d')
DATE1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

config = pathlib.Path.home() / '.config/youtube-dl-s/youtube_dl_s.json'

with open(config, 'r', encoding='utf-8') as target:
    config = json.load(target)

config['rss_opts']['output'] = config['YOUTUBR_DL_WL']

config['dl_opts']['output'] = config['YOUTUBR_DL_WL']
config['dl_opts']['data'] = config['YOUTUBR_DL_DATA']

config['ydl_opts']['outtmpl'] = f"{config['YOUTUBR_DL_WL']}{DATE}/%(id)s/%(id)s.%(ext)s"


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-nor",
        "--norandom",
        action='store_true',
        help='désactive le random')
    parser.add_argument(
        "--skip-download",
        action='store_true', dest='skip_download',
        help='Do not download the video')
    parser.add_argument(
        "--refresh-xml",
        action='store_true', dest='refresh_xml',
        help='forces the refresh')
    parser.add_argument(
        "-v",
        "--verbose",
        action='store_true',
        help='debug')
    return parser.parse_args()


def diffFunc():
    import difflib
    import glob
    import sys

    FILELIST = config['YOUTUBR_DL_DATA'] + "filelist"
    cur_files = "\n".join(
        glob.glob(f"{config['YOUTUBR_DL_WL']}*/*"))

    try:
        with open(FILELIST, "r", encoding='utf-8') as fichier:
            fichier = str(fichier.read())
    except Exception as e:
        with open(FILELIST, "w", encoding='utf-8') as fichier:
            fichier = ''

    if fichier != cur_files:
        logging.info("[rss]")
        ls.rss(config['rss_opts'])
        dif = difflib.unified_diff(
            fichier.splitlines(),
            cur_files.splitlines(),
            n=0
        )
        logging.info('[diff] \n' + '\n'.join(dif))
        with open(FILELIST, "w", encoding='utf-8') as fichier:
            fichier.write(cur_files)


def rmFunc():
    # https://stackoverflow.com/questions/185936/how-to-delete-the-contents-of-a-folder-in-python
    import os
    import shutil

    folder = config['YOUTUBR_DL_WL'] + "trash/"

    try:
        os.listdir(folder)
    except Exception as e:
        logging.error(e)
        os.makedirs(os.path.dirname(folder))  # creating directories

    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                logging.info(file_path)
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                logging.info(file_path)
                shutil.rmtree(file_path)
        except Exception as e:
            logging.error(e)

    logging.info("[supprimer] ok")


def youtube_dlFunc():
    from youtube_dl_s import downloaders
    downloaders.YoutubeDLDownloader(config['ydl_opts'], downloaders.feedparser1(config['dl_opts']))
    if config['watchlater']:
        downloaders.YoutubeDLWatchlater(config['ydl_opts'])


def test_youtube():
    # https://stackoverflow.com/questions/177389/testing-socket-connection-in-python
    # http://www.techniqal.com/2011/01/26/simple-socket-connection-test-in-python-3/
    host = 'www.youtube.com'
    port = 443

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            s.shutdown(2)
            logging.info("[connect] Success connecting to " + host)
            return True
        except socket.error as e:
            logging.error("[connect] Cannot connect to " + host)
            logging.error(e)
        finally:
            s.close()


def get_lock():
    # https://stackoverflow.com/questions/788411/check-to-see-if-python-script-is-running/7758075#7758075

    with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as _lock_socket:
        try:
            _lock_socket.bind('\0' + "watchlater")
        except Exception as e:
            logging.error('[lock] exists')
            logging.error(e)
            exit(0)


def timeFunc():
    import random
    import time

    MIN = 1
    MAX = 3420

    number = random.randint(MIN, MAX)
    number1 = str(datetime.timedelta(seconds=number))

    logging.info(f"[sleep] dans {str_number}")
    time.sleep(number)
    logging.debug("[sleep] ok")


def main():
    args = parse_arguments()

    # verbose
    if args.verbose:
        logging.basicConfig(
            format='%(asctime)s %(message)s',
            filename=config['logfile'],
            level=logging.DEBUG)
    else:
        logging.basicConfig(
            format='%(asctime)s %(message)s',
            filename=config['logfile'],
            level=logging.INFO)

    # refreshxml
    if args.refresh_xml:
        logging.info("[rss] refresh")
        ls.rss(config['rss_opts'])

    # random
    if not args.norandom:
        timeFunc()

    if args.skip_download:
        config['ydl_opts']['skip_download'] = True

    get_lock()
    if test_youtube():
        youtube_dlFunc()
        rmFunc()
        diffFunc()
        logging.info("[fin] " + DATE1)


if __name__ == '__main__':
    main()
