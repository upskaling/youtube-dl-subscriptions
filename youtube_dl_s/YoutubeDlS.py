#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from youtube_dl_s import ls
import argparse
import datetime
import json
import logging
import os
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
        "--purge",
        action='store_true',
        help='purge')
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


def getsize(path):
    fichier = []
    for root, dirs, files in os.walk(path):
        for i in files:
            fichier.append(os.path.join(root, i))
    return sum([os.path.getsize(i) for i in fichier])


def purge(path):
    for video in pathlib.Path(path).glob('*'):

        head, tail = os.path.split(video)
        if tail in ['index.xml']:
            continue

        modified_time = now - \
            datetime.datetime.utcfromtimestamp(os.path.getmtime(video))
        if modified_time > datetime.timedelta(
                days=config['YOUTUBR_DL_WL_purge_days']):
            print(f'{modified_time} Removing: {str(video)}')
            os.rename(
                video,
                pathlib.Path(
                    config['YOUTUBR_DL_WL'],
                    "trash/",
                    os.path.basename(video)
                )
            )
            # video.unlink()


def rmFunc():
    # https://stackoverflow.com/questions/185936/how-to-delete-the-contents-of-a-folder-in-python
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

    if config['watchlater']:
        downloaders.YoutubeDLDownloader(
            config['ydl_opts'],
            ['https://www.youtube.com/playlist?list=WL'])

    def removeDuplicates(data):
        h = []
        result = []
        for i in data:
            if i['url'] not in h:
                h += [i['url']]
                result += [i]
        return result

    with open(config['errorsfile'], 'r') as target:
        try:
            errorslines = json.load(target)
        except json.decoder.JSONDecodeError:
            errorslines = []

    feedurl = downloaders.feedparser1(config['dl_opts'])
    if feedurl:
        listurl = []
        for i in feedurl:
            data1 = {}
            data1['url'] = i
            data1['update'] = DATE1
            data1['pass'] = 0
            listurl += [data1]
    else:
        listurl = []

    listurl += errorslines
    listurl = removeDuplicates(listurl)

    md = 0
    for i in listurl:
        if i['pass'] >= config['errorspass']:
            i['pass'] += 1
            continue
        md += 1
        if md <= config['max_downloads']:
            if downloaders.YoutubeDLDownloader(config['ydl_opts'], [i['url']]):
                i['pass'] += 1
            else:
                listurl.remove(i)

    with open(config['errorsfile'], 'w') as target:
        json.dump(listurl, target, indent=2)


def test_youtube():
    # https://stackoverflow.com/questions/177389/testing-socket-connection-in-python
    # http://www.techniqal.com/2011/01/26/simple-socket-connection-test-in-python-3/
    host = 'www.youtube.com'
    port = 443

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            logging.info(f"[connect] Success connecting to {host}")
            return True
        except Exception as e:
            logging.error(
                f"[connect] Cannot connect to {host} Exception is {e}")
        finally:
            s.close()


def get_lock(process_name):
    # https://stackoverflow.com/questions/788411/check-to-see-if-python-script-is-running/7758075#7758075

    get_lock._lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    try:
        get_lock._lock_socket.bind('\0' + process_name)
    except Exception as e:
        logging.error(f'[lock] {e}')
        exit(0)


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

    # purge
    if args.purge:
        rm_opts = config['YOUTUBR_DL_WL']
        print(getsize(rm_opts))
        if getsize(rm_opts) > config['YOUTUBR_DL_WL_purge']:
            purge(rm_opts)
        return

    if args.skip_download:
        config['ydl_opts']['skip_download'] = True

    get_lock('youtube-dl-subscriptions')
    if test_youtube():
        youtube_dlFunc()
        rmFunc()
        diffFunc()
        logging.info("[fin] " + DATE1)


if __name__ == '__main__':
    main()
