#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glob
import json
import mimetypes
import os
import logging
from time import gmtime, strftime, localtime, ctime

from xml.dom import minidom
# from PIL import Image
# from PIL.ExifTags import TAGS
# from xml.dom.minidom import Node

DATE = strftime("%a, %d %b %Y %H:%M:%S +0200", localtime())
# print(DATE)

# ---------------------------


def rejson(arg):
    # ~print(arg)

    rejson = {}
    with open(arg) as json_file:
        data = json.load(json_file)
        rejson['upload_date'] = str(data.get("upload_date", "None"))
        rejson['json_id'] = str(data.get("id", "None"))
        rejson['webpage_url'] = str(data.get("webpage_url", "None"))
        rejson['thumbnail'] = str(data.get("thumbnail", "None"))
        rejson['json_title'] = str(data.get("title", "None"))
        rejson['view_count'] = str(data.get("view_count", "None"))
        rejson['uploader'] = str(data.get("uploader", "None"))
        rejson['channel_url'] = str(data.get("channel_url", "None"))
        json_description = str(data.get("description", "None"))
        rejson['json_description'] = json_description.replace('\n', '<br>')

    return rejson


def rss(rss_opts):
    doc = minidom.Document()

    rss = doc.createElement('rss')
    rss.setAttribute("version", "2.0")
    doc.appendChild(rss)

    channel = doc.createElement('channel')
    rss.appendChild(channel)

    title = doc.createElement('title')
    text = doc.createTextNode(rss_opts['title'])
    title.appendChild(text)
    channel.appendChild(title)

    link = doc.createElement('link')
    text = doc.createTextNode(rss_opts['URL'] + rss_opts['outtmpl'])
    link.appendChild(text)
    channel.appendChild(link)

    description = doc.createElement('description')
    text = doc.createTextNode(rss_opts['title'])
    description.appendChild(text)
    channel.appendChild(description)

    lastBuildDate = doc.createElement('lastBuildDate')
    text = doc.createTextNode(DATE)
    lastBuildDate.appendChild(text)
    channel.appendChild(lastBuildDate)

    LS = glob.glob(rss_opts['data'] + "/*/*/*.info.json")

    # print(sorted(LS))
    # ~print(len(LS))

    for name in sorted(LS):
        # ~if '.info.json' in name[-10:]:
        LSbasename = os.path.basename(name)  # id + .info.json
        LSdirname = os.path.dirname(name).replace(
            rss_opts['data'], "")  # fichier parents
        name_mp4 = name.replace('.info.json', '.mp4')

        exists = os.path.isfile(name_mp4)
        if exists:
            LSmimetypes = mimetypes.guess_type(name_mp4)[0]  # mimetypes
            LSgetsize = str(os.path.getsize(name_mp4))  # getsize
            LSbasename = os.path.basename(name_mp4)  # id + .mp4
            # date
            dt = os.path.getmtime(name_mp4)
            t_str = ctime(dt)
            LSgetctime = strftime(
                "%a, %d %b %Y %H:%M:%S %z", localtime(dt))
        else:
            LSmimetypes = ''  # mimetypes
            LSgetsize = ''  # getsize
            LSbasename = os.path.basename(name)  # id + .mp4
            LSgetctime = ''

        # ~print(name)
        # ~print(os.path.dirname(name))
        # ~print(LSbasename)
        # -----------------------------
        jsonb = rejson(name)

        if jsonb['thumbnail'] == 'None':
            poster = ''
        else:
            poster = f"poster=\"{jsonb['thumbnail']}\""

        item = doc.createElement('item')

        title = doc.createElement('title')
        text = doc.createCDATASection(jsonb['json_title'])
        title.appendChild(text)
        item.appendChild(title.cloneNode(True))

        link = doc.createElement('link')
        text = doc.createTextNode(f"{rss_opts['URL']}{LSdirname}/{LSbasename}")
        link.appendChild(text)
        item.appendChild(link.cloneNode(True))

        guid = doc.createElement('guid')
        text = doc.createTextNode(f"{rss_opts['URL']}{LSdirname}/{LSbasename}")
        guid.setAttribute('isPermaLink', 'false')
        guid.appendChild(text)
        item.appendChild(guid.cloneNode(True))

        description = doc.createElement('description')
        description_rv = f"""<video width="100%" preload="metadata" controls {poster}>
        <source src="{rss_opts['URL']}{LSdirname}/{LSbasename}" type="{LSmimetypes}">
        Votre navigateur ne permet pas de lire les vidéos HTML5.
        </video><br>
        <a title="{jsonb['json_title']}" href="{jsonb['webpage_url']}">{jsonb['json_title']}</a><br>
        <p>{jsonb['view_count']} vues</p>
        <p>{jsonb['uploader']}</p>
        <p><strong>Comment:</strong></p>
        <p>{jsonb['json_description']}</p>"""
        text = doc.createCDATASection(description_rv)
        description.setAttribute('type', 'html')
        description.appendChild(text)
        item.appendChild(description.cloneNode(True))

        pubDate = doc.createElement('pubDate')
        text = doc.createTextNode(LSgetctime)
        pubDate.appendChild(text)
        item.appendChild(pubDate.cloneNode(True))

        enclosure = doc.createElement('enclosure')
        enclosure.setAttribute(
            "url", f"{rss_opts['URL']}{LSdirname}/{LSbasename}")
        enclosure.setAttribute("length", LSgetsize)
        enclosure.setAttribute("type", LSmimetypes)
        item.appendChild(enclosure.cloneNode(True))

        author = doc.createElement('author')
        text = doc.createCDATASection(jsonb['uploader'])
        author.appendChild(text)
        item.appendChild(author.cloneNode(True))

        channel.appendChild(item)

    with open(rss_opts['data'] + rss_opts['outtmpl'], "w", encoding='utf-8') as fichier:
        xml_str = doc.toprettyxml(indent="  ")
        fichier.write(xml_str)
        pass

# print(LSexiftool)
# print(":: type",type(LSexiftool))


if __name__ == "__main__":
    rss_opts = {
        'outtmpl': 'index.xml',
        'data': './data/watchlater/',
        'title': 'watchlater',
        'URL': '<URL>'
    }

    rss(rss_opts)
