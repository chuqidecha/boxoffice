# -*- coding: utf-8 -*-

import csv

from BoxOffice.items import BoxOfficeItem


class CsvPipeline(object):
    writer = []
    keys = []
    csvfile = []
    keys = ["film_name", "director", "actors", "broadcast_time", "country", "time_span", "category", "language",
            "box_office"]

    def open_spider(self, spider):
        self.csvfile = open("test.csv", "w")
        self.writer = csv.writer(self.csvfile)
        self.writer.writerow(self.keys)

    def process_item(self, item, spider):
        self.writer.writerow([str(item[key]) for key in self.keys])

    def close_spider(self, spider):
        self.csvfile.close()
