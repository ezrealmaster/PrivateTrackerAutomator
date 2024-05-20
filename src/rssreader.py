import logging as log
import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup


class RSSReader:
    def __init__(self, rss_feed):
        self.rss_feed = rss_feed

        feed = self.get_feed_soup()
        self.last_post_date = self.parse_date(feed.pubDate.string)
        log.debug(f"RSSReader initialized. Last post: {self.last_post_date}")

    def parse_date(self, datestr):
        return datetime.strptime(datestr, "%a, %d %b %Y %H:%M:%S %z")

    def get_feed_soup(self):
        while True:
            r = requests.get(self.rss_feed)
            if r.status_code == requests.codes.ok:
                break
            log.debug("Could not request xml.")
            time.sleep(10)
        return BeautifulSoup(r.content, "lxml")

    def poll_for_new(self):
        feed = self.get_feed_soup()

        new_posts_id = []
        new_last_date = None
        for item in feed.findAll("item"):
            item_date = self.parse_date(item.pubDate.string)
            if item_date > self.last_post_date:
                log.debug(f"Object with id {item.guid.string} posted at: ´{item_date}")
                new_posts_id.append(str(item.guid.string))
                if new_last_date is None:
                    new_last_date = item_date
            else:
                break
        if new_last_date is not None:
            self.last_post_date = new_last_date

        if len(new_posts_id) > 0:
            return new_posts_id
