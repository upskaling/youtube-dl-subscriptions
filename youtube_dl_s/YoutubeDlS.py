#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import downloaders
import ls
import argparse
import datetime
import json
import logging
import logging.handlers
import os
import pathlib
import socket
import sys

logger = logging.getLogger()

now = datetime.datetime.now()

date = datetime.datetime.now().strftime('%Y-%m-%d')
datehour = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

config = pathlib.Path.home() / '.config/youtube-dl-s/youtube_dl_s.json'

with open(config, 'r', encoding='utf-8') as target:
    config = json.load(target)

config['rss_opts']['output'] = config['YOUTUBR_DL_WL']

config['dl_opts']['output'] = config['YOUTUBR_DL_WL']
config['dl_opts']['data'] = config['YOUTUBR_DL_DATA']

config['ydl_opts']['outtmpl'] = \
    f"{config['YOUTUBR_DL_WL']}{date}/%(id)s/%(id)s.%(ext)s"


class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass


def parse_arguments():
    """Parse arguments."""
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)

    g = parser.add_mutually_exclusive_group()
    g.add_argument(
        "--debug", "-d", action="store_true",
        default=False,
        help="enable debugging")
    g.add_argument(
        "--silent", "-s", action="store_true",
        default=False,
        help="don't log")
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
        "--refresh-html",
        action='store_true', dest='refresh_html',
        help='forces the refresh')

    return parser.parse_args()


def setup_logging(options):
    """Configure logging."""
    root = logging.getLogger("")
    root.setLevel(logging.WARNING)
    logger.setLevel(options.debug and logging.DEBUG or logging.INFO)
    if not options.silent:
        if not sys.stderr.isatty():
            facility = logging.handlers.SysLogHandler.LOG_DAEMON
            sh = logging.handlers.SysLogHandler(address='/dev/log',
                                                facility=facility)
            sh.setFormatter(logging.Formatter(
                "{0}[{1}]: %(message)s".format(
                    logger.name,
                    os.getpid())))
            root.addHandler(sh)
        else:
            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter(
                "%(levelname)s[%(name)s] %(message)s"))
            root.addHandler(ch)


def diffFunc():
    import difflib
    import glob

    FILELIST = config['YOUTUBR_DL_DATA'] + "filelist"
    cur_files = "\n".join(
        glob.glob(f"{config['YOUTUBR_DL_WL']}*/*"))

    try:
        with open(FILELIST, "r", encoding='utf-8') as fichier:
            fichier = str(fichier.read())
    except Exception:
        with open(FILELIST, "w", encoding='utf-8') as fichier:
            fichier = ''

    if fichier != cur_files:
        logger.info("[rss]")
        ls.rss(config['rss_opts'])
        if config['html']:
            logger.info("[html]")
            ls.html(config['rss_opts'])
        dif = difflib.unified_diff(
            fichier.splitlines(),
            cur_files.splitlines(),
            n=0
        )
        logger.info('[diff] \n' + '\n'.join(dif))
        with open(FILELIST, "w", encoding='utf-8') as fichier:
            fichier.write(cur_files)


def getsize(path):
    fichier = []
    for root, _, files in os.walk(path):
        for i in files:
            fichier.append(os.path.join(root, i))
    return sum([os.path.getsize(i) for i in fichier])


def purge(path):
    for video in pathlib.Path(path).glob('*'):

        _, tail = os.path.split(video)
        if tail in ['style.css', 'favicon.png', 'index.xml', 'index.html']:
            continue

        modified_time = now - \
            datetime.datetime.utcfromtimestamp(os.path.getmtime(video))
        if modified_time > datetime.timedelta(
                days=config['YOUTUBR_DL_WL_purge_days']):
            logger.info(f'{modified_time} Removing: {str(video)}')
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
        logger.exception(e)
        os.makedirs(os.path.dirname(folder))  # creating directories

    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                logger.info(file_path)
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                logger.info(file_path)
                shutil.rmtree(file_path)
        except Exception as e:
            logger.exception(e)

    logger.info("[supprimer] ok")


class list_of_videos_to_watch():

    def __init__(self):
        self.listURL = []
        self.read()

    def get(self):
        return self.listURL

    def read(self):
        try:
            with open(config['errorsfile'], 'r') as target:
                self.listURL += json.load(target)
        except json.decoder.JSONDecodeError as e:
            message = 'json.decoder.JSONDecodeError:', e
            logger.exception(message)
        except FileNotFoundError as e:
            message = 'FileNotFoundError:', e
            logger.exception(message)

    def feedparser1(self):
        self.listURL += downloaders.feedparser1(config['dl_opts'])

    def removeDuplicates(self):
        h = []
        self.result = []
        for i in self.listURL:
            if i['url'] not in h:
                h.append(i['url'])
                self.result.append(i)
        self.listURL = self.result

    def Sorted(self):
        self.listURL = sorted(self.listURL, key=lambda k: k['update'])
        self.writing()

    def writing(self):
        with open(config['errorsfile'], 'w') as target:
            json.dump(self.listURL, target, indent=2)

    def downloader(self):
        md = 0
        for i in self.listURL[:]:

            if not md <= config['max_downloads']:
                break

            if i['pass'] >= config['errorspass']:
                continue

            if downloaders.YoutubeDLDownloader(config['ydl_opts'], [i['url']]):
                i['pass'] += 1
            else:
                md += 1
                self.listURL.remove(i)

        self.writing()


def test_youtube():
    # https://stackoverflow.com/questions/177389/testing-socket-connection-in-python
    # http://www.techniqal.com/2011/01/26/simple-socket-connection-test-in-python-3/
    host = 'www.youtube.com'
    port = 443

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            logger.info(f"[connect] Success connecting to {host}")
            return True
        except Exception as e:
            logger.exception(
                f"[connect] Cannot connect to {host} Exception is {e}")
        finally:
            s.close()


def get_lock(process_name):
    # https://stackoverflow.com/questions/788411/check-to-see-if-python-script-is-running/7758075#7758075

    get_lock._lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    try:
        get_lock._lock_socket.bind('\0' + process_name)
    except Exception as e:
        logger.exception(f'[lock] {e}')
        exit(0)


def YoutubeDLS(options):
    # refreshxml
    if options.refresh_xml:
        ls.rss(config['rss_opts'])

    # refreshhml
    if options.refresh_html:
        ls.html(config['rss_opts'])

    # purge
    if options.purge:
        print(getsize(config['YOUTUBR_DL_WL']))
        purge(config['YOUTUBR_DL_WL'])
        return

    if getsize(config['YOUTUBR_DL_WL']) > config['YOUTUBR_DL_WL_purge']:
        logger.info(f"[purge]")
        purge(config['YOUTUBR_DL_WL'])

    if options.skip_download:
        config['ydl_opts']['skip_download'] = True

    get_lock('youtube-dl-subscriptions')
    if test_youtube():
        if config['watchlater']:
            downloaders.YoutubeDLDownloader(
                config['ydl_opts'],
                ['https://www.youtube.com/playlist?list=WL'])

        laus = list_of_videos_to_watch()
        laus.feedparser1()
        laus.removeDuplicates()
        laus.Sorted()
        if not options.skip_download:
            laus.downloader()

        rmFunc()
        diffFunc()
        logger.info("[fin] " + datehour)


def main():
    options = parse_arguments()
    setup_logging(options)

    try:
        YoutubeDLS(options)
    except Exception as e:
        logger.exception("%s", e)
        # exit(1)
    exit(0)
    pass


if __name__ == '__main__':
    main()
