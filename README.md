# youtube-dl-subscriptions

## INSTALLATION

~/.config/youtube-dl-s/youtube_dl_s.json
```
{
  "errorsfile": "./data/errorsfile.json",
  "errorspass": 10,
  "logfile": "./data/ytwatchlater.log",
  "max_downloads": 15,
  "watchlater": false,
  "YOUTUBR_DL_DATA": "./data/",
  "YOUTUBR_DL_WL": "./data/watchlater/",
  "YOUTUBR_DL_WL_purge": 215000000,
  "YOUTUBR_DL_WL_purge_days": 6,
  "dl_opts": {
    "json_file": "./data/feeds.json"
    },
  "rss_opts": {
    "in_html": "./templates/index.html",
    "out_html": "index.html",
    "out_xml": "index.xml",
    "title": "watchlater",
    "URL": "https://<URL>/"
    },
  "ydl_opts": {
    "cookiefile": "./data/cookies2.txt",
    "download_archive": "./data/archive-WL.txt",
    "format": "[height<=?720][ext=mp4]/best",
    "is_live": false,
    "mark_watched": true,
    "max_filesize": 1200000000,
    "writeinfojson": true
  }
}
```

feeds.json
```
{
  "outline": [
    {
      "xmlUrl": "https://www.youtube.com/feeds/videos.xml?channel_id=<UUID>",
      "title": "<title>",
      "update_interval": 86400,
      "update": "2010-12-30 23:00:00"
    },
    {
      "xmlUrl": "https://peertube.fr/feeds/videos.xml?accountId=<UUID>",
      "title": "<title>",
      "update_interval": 86400,
      "update": "2010-12-30 23:00:00"
    }
  ]
}
```

### opml to json

https://www.youtube.com/subscription_manager

```
python3 youtube_dl_s/opmltojson.py
```

### crontab

```
0 */1 * * * python3 /path/to/youtube-dl-subscriptions/youtube_dl_s/YoutubeDlS.py
```

## see also

- https://euandre.org/2018/12/21/using-youtube-dl-to-manage-youtube-subscriptions.html
- https://www.reddit.com/r/DataHoarder/comments/9sg8q5/i_built_a_selfhosted_youtube_subscription_manager/

- https://github.com/chibicitiberiu/ytsm
- https://github.com/mewfree/youtube-dl-subscriptions
- https://github.com/sawyerf/Youtube_subscription_manager
- https://github.com/yazgoo/youtube-subscriptions


## RESOURCES

- https://github.com/rg3/youtube-dl/blob/master/README.md
