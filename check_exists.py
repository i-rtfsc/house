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

import os

import dataset
import requests


def main(file_name, districts):
    file = os.path.join(os.path.dirname(__file__), "data", file_name)
    if not os.path.exists(file):
        return

    path = os.path.join(file)
    database = dataset.connect('sqlite:///' + path)

    for district in districts:
        table = database[district]
        for data in table.all():
            house_id = data['house_id']
            house_url = data['house_url']
            response = requests.get(house_url)
            if response.status_code == 404:
                print('id = ',  house_id, ' url = ', house_url)
                table.delete(house_id=house_id)


    database.close()
    print("done")


if __name__ == "__main__":
    file_name = 'sh-sf1a3a4a5p3-lianjia.db'
    districts = ["pudong", "minhang", "baoshan", "songjiang", "jiading", "qingpu"]
    main(file_name, districts)
