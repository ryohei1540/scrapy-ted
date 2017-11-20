# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class TedItem(Item):
    title = Field()
    published_date = Field()
    time = Field()
    views = Field()
    tags = Field()
    person = Field()
    content = Field()
    url = Field()
