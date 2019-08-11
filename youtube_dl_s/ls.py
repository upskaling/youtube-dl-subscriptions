#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glob
import json
import mimetypes
import os
import logging
from time import gmtime, strftime, localtime, ctime
from xml.dom import minidom

logger = logging.getLogger()

datehour = strftime("%a, %d %b %Y %H:%M:%S +0200", localtime())


def rejson(json_path):

    rejson = dict()
    with open(json_path) as json_file:
        data = json.load(json_file)

    for i in data:
        rejson[i] = data.get(i, "None")

    if data.get('uploder_url'):
        rejson['uploader_url'] = data.get('uploder_url', "None")

    json_description = str(data.get("description", "None"))
    rejson['json_description'] = json_description.replace('\n', '<br>')

    return rejson


class FeedEntry(object):
    """ Class doc """

    def __init__(self):
        """ Class initialiser """
        self.doc = minidom.Document()
        self.item = self.doc.createElement('item')
        pass

    def title(self, title=None):
        text = self.doc.createCDATASection(title)
        titleCE = self.doc.createElement('title')
        titleCE.appendChild(text)
        self.item.appendChild(titleCE)

    def link(self, link=None):
        text = self.doc.createTextNode(link)
        linkCE = self.doc.createElement('link')
        linkCE.appendChild(text)
        self.item.appendChild(linkCE)

    def guid(self, guid=None, permalink=False):
        text = self.doc.createTextNode(guid)
        guidCE = self.doc.createElement('guid')
        if permalink:
            guidCE.setAttribute('isPermaLink', 'trus')
        else:
            guidCE.setAttribute('isPermaLink', 'false')
        guidCE.appendChild(text)
        self.item.appendChild(guidCE)

    def description(self, description=None):
        text = self.doc.createCDATASection(description)
        descriptionCE = self.doc.createElement('description')
        descriptionCE.setAttribute('type', 'html')
        descriptionCE.appendChild(text)
        self.item.appendChild(descriptionCE)

    def pubDate(self, pubDate=None):
        text = self.doc.createTextNode(pubDate)
        pubDateCE = self.doc.createElement('pubDate')
        pubDateCE.appendChild(text)
        self.item.appendChild(pubDateCE)

    def enclosure(self, url=None, length=None, type=None):
        enclosureCE = self.doc.createElement('enclosure')
        enclosureCE.setAttribute("url", url)
        enclosureCE.setAttribute("length", length)
        enclosureCE.setAttribute("type", type)
        self.item.appendChild(enclosureCE)

    def author(self, author=None):
        text = self.doc.createCDATASection(author)
        authorCE = self.doc.createElement('author')
        authorCE.appendChild(text)
        self.item.appendChild(authorCE)

    def category(self, category=None):
        for tags in category:
            text = self.doc.createCDATASection(tags)
            categoryCE = self.doc.createElement('category')
            categoryCE.appendChild(text)
            self.item.appendChild(categoryCE)

    def gen(self):
        return self.item


class FeedGenerator(object):
    """ Class doc """

    def __init__(self):
        """ Class initialiser """
        self.doc = minidom.Document()
        pass

    def m0(self, rss_opts):
        rss = self.doc.createElement('rss')
        rss.setAttribute("version", "2.0")
        self.doc.appendChild(rss)

        self.channel = self.doc.createElement('channel')
        rss.appendChild(self.channel)

        title = self.doc.createElement('title')
        text = self.doc.createTextNode(rss_opts['title'])
        title.appendChild(text)
        self.channel.appendChild(title)

        link = self.doc.createElement('link')
        text = self.doc.createTextNode(rss_opts['URL'] + rss_opts['out_xml'])
        link.appendChild(text)
        self.channel.appendChild(link)

        description = self.doc.createElement('description')
        text = self.doc.createTextNode(rss_opts['title'])
        description.appendChild(text)
        self.channel.appendChild(description)

        lastBuildDate = self.doc.createElement('lastBuildDate')
        text = self.doc.createTextNode(datehour)
        lastBuildDate.appendChild(text)
        self.channel.appendChild(lastBuildDate)

    def add_entry(self):
        feedEntry = FeedEntry()
        self.channel.appendChild(feedEntry.gen())
        return feedEntry

    def m1(self):
        return self.doc.toprettyxml(indent="  ")


def rss(rss_opts):
    logger.info("[rss] refresh")
    fg = FeedGenerator()
    fg.m0(rss_opts)

    for name in glob.iglob(rss_opts['output'] + '/*/*/*.info.json'):
        jsonb = rejson(name)

        LSdirname, LSbasename = os.path.split(name)  # id + .info.json
        LSdirname = LSdirname.replace(
            rss_opts['output'], '')  # fichier parents

        if os.path.isfile(jsonb['_filename']):
            LSmimetypes = mimetypes.guess_type(jsonb['_filename'])[0]
            LSgetsize = str(os.path.getsize(jsonb['_filename']))  # getsize
            LSbasename = os.path.basename(jsonb['_filename'])  # id + .mp4
            # date
            LSgetctime = os.path.getmtime(jsonb['_filename'])
            LSgetctime = strftime(
                "%a, %d %b %Y %H:%M:%S %z", localtime(LSgetctime))
        else:
            # ~continue
            LSmimetypes = ''  # mimetypes
            LSgetsize = ''  # getsize
            LSbasename = os.path.basename(name)  # id + .mp4
            LSgetctime = ''

        if jsonb['thumbnail'] == 'None':
            poster = ''
        else:
            poster = f"poster=\"{jsonb['thumbnail']}\""

        fe = fg.add_entry()
        fe.title(jsonb['title'])
        fe.link(f"{rss_opts['URL']}{LSdirname}/{LSbasename}")
        fe.guid(f"{rss_opts['URL']}{LSdirname}/{LSbasename}")
        fe.description(
            f"""<video width="100%" preload="metadata" controls {poster}>
        <source src="{rss_opts['URL']}{LSdirname}/{LSbasename}" type="{LSmimetypes}">
        Votre navigateur ne permet pas de lire les vidéos HTML5.
        </video><br>
        <a title="{jsonb['title']}" href="{jsonb['webpage_url']}">{jsonb['title']}</a><br>
        <p>{jsonb['view_count']} vues</p>
        <hr>
        <a href="{jsonb['uploader_url']}">{jsonb['uploader']}</a>
        <p>{jsonb['json_description']}</p>""")
        fe.pubDate(LSgetctime)
        fe.enclosure(
            f"{rss_opts['URL']}{LSdirname}/{LSbasename}",
            LSgetsize,
            LSmimetypes)
        fe.author(jsonb['uploader'])
        fe.category(jsonb['tags'])

    with open(rss_opts['output'] + rss_opts['out_xml'], "w", encoding='utf-8') as fichier:
        fichier.write(fg.m1())
        pass


if __name__ == "__main__":
    rss_opts = {
        'out_xml': 'index.xml',
        'output': './data/watchlater/',
        'title': 'watchlater',
        'URL': '<URL>'
    }

    rss(rss_opts)
