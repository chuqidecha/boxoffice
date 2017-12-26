# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import logging
import scrapy
from scrapy import Field


class BoxOfficeItem(scrapy.Item):
    film_name = Field()
    director = Field()
    actors = Field()
    broadcast_time = Field()
    country = Field()
    time_span = Field()
    category = Field()
    language = Field()
    box_office = Field()

