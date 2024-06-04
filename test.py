#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
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

import json
from datetime import datetime

import dataset
import os

def test():
    directory = os.path.join(os.path.dirname(__file__), "data")
    if not os.path.exists(directory):
        os.makedirs(directory)

    path = os.path.join(directory, 'sh-sf1a3a4a5p3-lianjia-old.db')
    database = dataset.connect('sqlite:///' + path)

    new_path = os.path.join(directory, 'sh-sf1a3a4a5p3-lianjia.db')
    new_database = dataset.connect('sqlite:///' + new_path)

    districts = ["pudong", "minhang", "baoshan", "songjiang", "jiading", "qingpu"]
    for district in districts:
        table = database[district]
        new_table = new_database[district]
        for old_data in table.all():
            data = dict()
            data['id'] = old_data['id']
            data['house_id'] = old_data['house_id']
            data['house_url'] = old_data['house_url']
            data['title'] = old_data['title']
            data['total_price'] = old_data['total_price']
            data['unit_price'] = old_data['unit_price']
            data['district'] = old_data['district']
            data['bizcircle'] = old_data['bizcircle']
            data['xiaoqu'] = old_data['xiaoqu']
            data['xiaoqu_id'] = old_data['xiaoqu_id']
            #room
            data['layout'] = old_data['layout']
            data['flood'] = old_data['flood']
            data['_building_area'] = old_data['_building_area']
            data['building_area'] = old_data['building_area']

            data['building_year'] = int(old_data['building_year'])

            data['structure'] = old_data['structure']
            data['house_area'] = old_data['house_area']
            data['building_type'] = old_data['building_type']
            data['orientation'] = old_data['orientation']
            data['building_structure'] = old_data['building_structure']
            data['decoration'] = old_data['decoration']
            data['house_elevator'] = old_data['house_elevator']
            data['elevator'] = old_data['elevator']
            data['listing_time'] = old_data['listing_time']
            data['house_characteristics'] = old_data['house_characteristics']
            data['last_deal'] = old_data['last_deal']
            data['land_usage'] = old_data['land_usage']
            data['deal_year'] = old_data['deal_year']
            data['ownership'] = old_data['ownership']
            data['mortgage'] = old_data['mortgage']
            data['annex'] = old_data['annex']

            data['follow_number'] = int(old_data['follow_number'])
            data['look_number'] = int(old_data['look_number'])

            data['crawl_time'] = old_data['crawl_time']
            data['page'] = old_data['page']
            data['total_count'] = old_data['total_count']
            data['current_count'] = old_data['current_count']
            data['update_time'] = old_data['update_time']

            price_trend = dict()
            price_trend[old_data['update_time'].split(" ")[0]] = data['total_price']
            data['price_trend'] = json.dumps(price_trend)
            new_table.insert(data)

    database.close()
    new_database.close()
    print("done")

def test2():
    directory = os.path.join(os.path.dirname(__file__), "data")
    if not os.path.exists(directory):
        os.makedirs(directory)

    path = os.path.join(directory, 'sh-sf1a3a4a5p3-lianjia-new.db')
    database = dataset.connect('sqlite:///' + path)
    table = database['songjiang']


    result = table.find_one(house_id='107105182917')
    data = dict(result)
    print(data)

    data['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    update_time = data['update_time'].split(" ")[0]
    print(update_time)
    total_price = data['total_price']
    print(total_price)

    price_trend_old = json.loads(data['price_trend'], object_hook=dict)
    price_trend_new = dict(sorted(price_trend_old.items()))
    for key, value in get_last_item(price_trend_new).items():
        # if value < result['total_price']:
        if value < 368.1:
            # price_trend_new[data['update_time'].split(" ")[0]] = result['total_price']
            # price_trend_new['2023-02-02'] = result['total_price']
            price_trend_new['2023-02-02'] = 368.1


    result['price_trend'] = json.dumps(price_trend_new)

    print(data)

    table.update(data, ['house_id'])

    database.close()

def get_last_item(dictionary):
    last_keyval = dictionary.popitem()
    dictionary.update({last_keyval[0]:last_keyval[1]})
    return {last_keyval[0]:last_keyval[1]}

def test3():
    price_trend = dict()

    price_trend['2023-01-18'] = 320
    price_trend['2022-12-15'] = 200
    result = json.dumps(price_trend)
    print(result)
    price_trend2 = json.loads(result, object_hook=dict)
    price_trend2['2023-01-15'] = 310
    price_trend_new = dict(sorted(price_trend2.items()))

    print(get_last_item(price_trend_new))

    for key, value in get_last_item(price_trend_new).items():
        print(key)
        print(value)
        if value < 390:
            price_trend_new['2023-02-02'] = 390

    result2 = json.dumps(price_trend_new)

    print(result2)

    print("2022-11-26 18:33:55".split(" ")[0])


def dict2list(price_trend):
    list_of_keys = []
    list_of_values = []
    for key, val in dict(sorted(price_trend.items())).items():
        list_of_keys.append(key)
        list_of_values.append(val)

    return list_of_keys, list_of_values
def test4():
    price_trend = {"2022-11-26": 360.0, "2023-02-15": 356.0, "2023-02-16": 352.0}

    list_of_keys, list_of_values = dict2list(price_trend)
    print(list_of_keys[0], list_of_values[0])
    print(list_of_keys[-1], list_of_values[-1])


def test5():
    import requests
    #https://sh.lianjia.com/ershoufang/107105798934.html
    response = requests.get('https://sh.lianjia.com/ershoufang/107106044971.html')
    print(response.status_code)
    if response.status_code == 200:
        print('Web site exists')
    else:
        print('Web site does not exist')


if __name__ == '__main__':
    # test()
    # test2()
    # test3()
    test5()