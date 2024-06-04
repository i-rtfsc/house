#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
import json
# Copyright (c) 2022 anqi.huang@outlook.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import dataset

from datetime import datetime
from scrapy.exceptions import DropItem
from scrapy import signals


class DBPipeline(object):

    def __init__(self):
        self.directory = os.path.join(os.path.join(os.path.dirname(__file__), "../"), "data")
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        self.database = None
        self.table = None

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        print("spider {} opened".format(spider.name))
        if spider.restrict:
            path = os.path.join(self.directory, '{}-{}-{}.db'.format(spider.city, spider.restrict, spider.name))
        else:
            path = os.path.join(self.directory, '{}-{}.db'.format(spider.city, spider.name))
        self.database = dataset.connect('sqlite:///' + path)
        self.table = self.database[spider.district]

    def spider_closed(self, spider):
        print("spider {} closed".format(spider.name))
        print(spider.restrict)
        self.database.close()

    def process_item(self, item, spider):
        result = self.table.find_one(house_id=item['house_id'])
        data = dict(item)
        # data['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        debug_info = "house id = {}, page = {} , count = {}/{} ".format(item['house_id'], item['page'],
                                                                        item['current_count'],
                                                                        item['total_count'])

        if result is not None:
            price_trend_old = json.loads(result['price_trend'], object_hook=dict)
            price_trend_old = dict(sorted(price_trend_old.items()))
            price_trend_new = price_trend_old

            last_keyval = price_trend_old.popitem()
            price_trend_old.update({last_keyval[0]: last_keyval[1]})

            for key, value in {last_keyval[0]: last_keyval[1]}.items():
                if value != item['total_price']:
                    price_trend_new[data['update_time'].split(" ")[0]] = item['total_price']
                    data['price_trend'] = json.dumps(price_trend_new)
                    print("update house id = {}, price trend = {}".format(item['house_id'], data['price_trend']))

            if spider.DEBUG:
                print("update->", debug_info)

            self.table.update(data, ['house_id'])
        else:
            data['crawl_time'] = data['update_time']
            price_trend = dict()
            price_time = data['crawl_time'].split(" ")[0].strip()
            price_trend[price_time] = data['total_price']
            data['price_trend'] = json.dumps(price_trend)

            if spider.DEBUG:
                print("init->", debug_info)

            self.table.insert(data)

        return item


class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['house_id'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['house_id'])
            return item
