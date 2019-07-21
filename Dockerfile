FROM alpine:3.9
LABEL maintainer="youtube-dl-subscriptions <https://github.com/upskaling/youtube-dl-subscriptions>" \
   description="youtube-dl + subscriptions = youtube-dl-subscriptions"

WORKDIR /usr/local/youtube-dl-s
ENTRYPOINT ["/sbin/tini","--","/usr/bin/python3","/usr/local/youtube-dl-s/youtube_dl_s/YoutubeDlS.py","-s"]

COPY requirements.txt ./requirements.txt

RUN apk -U upgrade \
   && apk add -t build-dependencies \
   build-base \
   python-dev \
   libffi-dev \
   openssl-dev \
   libxml2-dev \
   && apk add \
   python3 \
   python3-dev \
   libxml2 \
   libxslt \
   libxslt-dev \
   openssl \
   ca-certificates \
   tini \
   ffmpeg \
   && pip3 install --upgrade pip \
   && pip3 install --no-cache -r requirements.txt \
   && apk del build-dependencies \
   && rm -f /var/cache/apk/* \
   && adduser -D -h /usr/local/youtube-dl-s -s /bin/sh yt-dl-s yt-dl-s

COPY --chown=yt-dl-s:yt-dl-s . .

USER yt-dl-s
