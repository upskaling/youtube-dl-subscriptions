#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import glob
import json
import mimetypes
import os
import logging
from shutil import copy
from time import gmtime, strftime, localtime, ctime
from xml.dom import minidom

logger = logging.getLogger()

datehour = strftime("%a, %d %b %Y %H:%M:%S +0200", localtime())


def rejson(json_path):

    rejson = {}
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

    for name in glob.glob(rss_opts['output'] + '/*/*/'):

        jsonb = glob.glob(name + '*.info.json')

        if not jsonb:
            continue

        jsonb = rejson(jsonb[0])
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

        jpg_gg = glob.glob(name + '*.jpg')
        if jpg_gg:
            jsonb['thumbnail'] = jpg_gg[0].replace(rss_opts['output'], "")

        if jsonb['thumbnail'] is None:
            poster = ''
        else:
            poster = f"poster=\"{rss_opts['URL']}/{jsonb['thumbnail']}\""

        fe = fg.add_entry()
        fe.title(jsonb['title'])
        fe.link(f"{rss_opts['URL']}{LSdirname}/{LSbasename}")
        fe.guid(f"{rss_opts['URL']}{LSdirname}/{LSbasename}")
        fe.description(
            f"""<video width="100%" preload="metadata" controls {poster}>
        <source src="{rss_opts['URL']}{LSdirname}/{LSbasename}" """
            f"""type="{LSmimetypes}">
        Votre navigateur ne permet pas de lire les vidéos HTML5.
        </video><br>
        <a title="{jsonb['title']}" href="{jsonb['webpage_url']}">"""
            f"""{jsonb['title']}</a><br>
        <p>{jsonb['view_count']} vues</p>
        <hr>
        <a href="{jsonb['uploader_url']}" rel="author">{jsonb['uploader']}</a>
        <p>{jsonb['json_description']}</p>""")
        fe.pubDate(LSgetctime)
        fe.enclosure(
            f"{rss_opts['URL']}{LSdirname}/{LSbasename}",
            LSgetsize,
            LSmimetypes)
        fe.author(jsonb['uploader'])
        fe.category(jsonb['tags'])

    with open(rss_opts['output'] + rss_opts['out_xml'], "w",
              encoding='utf-8') as fichier:
        fichier.write(fg.m1())
        pass


def html(rss_opts):
    logger.info("[html] refresh")
    with open(rss_opts['in_html'], 'r', encoding='utf-8') as fichier:
        index_html = fichier.read()

    ps = []
    ggrss = glob.glob(rss_opts['output'] + "/*/")
    ggrss = sorted(ggrss)
    for date in ggrss:
        dirname = os.path.dirname(date).replace(rss_opts['output'], "")

        if dirname == "trash":
            continue

        video_list = glob.glob(date + "*/")

        ps.append(
            f"""<!-- {dirname} -->
    <h3 id="{dirname}" class="window-subtitle" >{dirname}
    <span class="video_list">({len(video_list)})</span></h3>
    <div class=pure-g>""")

        for name in video_list:

            jsonb = glob.glob(name + '*.info.json')

            if not jsonb:
                continue

            jsonb = rejson(jsonb[0])
            LSdirname = os.path.dirname(name).replace(
                rss_opts['output'], "")  # fichier parents

            if jsonb['duration'] >= 3600:
                jsonb['duration'] = strftime(
                    "%H:%M:%S", gmtime(jsonb['duration']))
            else:
                jsonb['duration'] = strftime(
                    "%M:%S", gmtime(jsonb['duration']))

            if os.path.isfile(jsonb['_filename']):
                url_video = LSdirname + "/" + \
                    os.path.basename(jsonb['_filename'])
                image1 = '''<div class="t-m">
                    <img class="tile__favicon"
                    src="favicon.png" width="16" height="16">
                local</div>'''
            else:
                url_video = jsonb['webpage_url']
                image1 = '''<div class="t-m">
                   <img class="tile__favicon"
                   src="youtube-logo.png" width="16" height="16">
                YouTube</div>'''

            jpg_gg = glob.glob(name + '*.jpg')
            if jpg_gg:
                jsonb['thumbnail'] = jpg_gg[0].replace(rss_opts['output'], "")

            if jsonb['thumbnail'] is None:
                poster = ''
            else:
                poster = f'''<img id="img" loading="lazy" class="thumbnail"'''\
                    f''' src="{jsonb['thumbnail']}" width="210">'''

            ps.append(f'''    <my-video-miniature>
        <div class="video-miniature">
            <a href="{url_video}">
                <div class="thumbnail">{poster}
                    <p class="length">{jsonb['duration']}</p>
                </div>
            </a>
            <div class="tile__body">
            <p>{jsonb['title']}</p>
            <a href="{jsonb['uploader_url']}" rel="author">
                <b>{jsonb['uploader']}</b></a>
            <p style="text-align:right">{jsonb['view_count']} vues</p>
            {image1}
            </div>
        </div>
    </my-video-miniature>''')
            pass

        ps.append("</div>")
        pass

    pss = '\n'.join(ps)
    with open(rss_opts['output'] + rss_opts['out_html'], 'w', encoding='utf-8'
              ) as fichier:
        fichier.write(index_html.format(video=pss, title=rss_opts['title']))

    output = os.path.abspath(rss_opts['output'])
    copy('./templates/style.css', output)
    copy('./templates/favicon.png', output)
    copy('./templates/youtube-logo.png', output)


if __name__ == "__main__":
    rss_opts = {
        'in_html': './templates/index.html',
        'out_html': 'index.html',
        'output': './data/watchlater/',
        'out_xml': 'index.xml',
        'title': 'watchlater',
        'URL': '<URL>'
    }

    rss(rss_opts)
    html(rss_opts)
