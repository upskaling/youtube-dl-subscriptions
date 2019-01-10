#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import opml
from datetime import datetime, timedelta

outline = opml.parse('subscription_manager')
urls = []
title = []
for i in range(0,len(outline[0])):
    urls.append(outline[0][i].xmlUrl)
    title.append(outline[0][i].title)

# ~print(title[1])
# ~print(urls[1])

json_file = "./feeds.json"

datetime_now = datetime.now()
update_interval = timedelta(seconds=-60)

# ~with open(json_file, 'r') as target:
    # ~data = json.load(target)

data = {}
data["outline"] = []
# ~data["outline"] = []
# ~data["outline"][1]["xmlUrl"] = urls[1]
# ~print(data3)

for i in range(0,len(urls)):
    datetime_now = update_interval + datetime_now
    date = datetime_now.strftime("%Y-%m-%d %H:%M:%S")
    data1 = {}
    data1["xmlUrl"] = urls[i]
    data1["title"] = title[i]
    data1["update_interval"] = 86400
    data1["update"] = date
    data["outline"] += [data1]


with open(json_file, 'w', encoding='utf-8') as target:
    json_data = json.dumps(data, indent=4)
    json.dump(data, target, indent=4)
    # ~print(json_data)

# ~print(urls)
print("::: ok")
