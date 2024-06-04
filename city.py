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


from house.base.net_utils import get_data


def get_city_info(city_id):
    """获取城市信息"""
    url = 'http://app.api.lianjia.com/config/config/initData'

    payload = {
        'params': '{{"city_id": {}, "mobile_type": "android", "version": "8.0.1"}}'.format(city_id),
        'fields': '{"city_info": "", "city_config_all": ""}'
    }

    data = get_data(url, payload, method='POST')

    city_info = None
    for a_city in data['city_info']['info']:
        print('{} = {}'.format(a_city['city_name'], a_city['city_id']))
        if str(a_city['city_id']) == city_id:
            city_info = a_city
            break

    for a_city in data['city_config_all']['list']:
        # print('{} = {} = {}'.format(a_city['city_name'], a_city['abbr'], a_city['city_id']))
        if str(a_city['city_id']) == city_id:
            city_info['city_abbr'] = a_city['abbr']
            break

    # print(city_info)
    return city_info


if __name__ == '__main__':
    city_id = "310000"
    city_info = get_city_info(city_id)
    city_district = dict()
    city_bizcircle = dict()

    test = ""

    for district in city_info['district']:

        district_quanpin = str(district['district_quanpin'])
        district_id = str(district['district_id'])
        if 'shanghaizhoubian' == district_quanpin:
            print("don't need shanghai zhou bian")
        else:
            # print('district_quanpin = {} , district_id = {}'.format(district_quanpin, district_id))
            print(' # {}'.format(district['district_name']))
            print(' # district = \'{}\''.format(district_quanpin))
            city_district[district_quanpin] = str(district_id)
            test +=  district_quanpin + "/"
            for bizcircle in district['bizcircle']:
                bizcircle_name = str(bizcircle['bizcircle_name'])
                bizcircle_id = str(bizcircle['bizcircle_id'])
                # print('bizcircle_name = {} , bizcircle_id = {}'.format(bizcircle_name, bizcircle_id))
                city_bizcircle[bizcircle_name] = str(bizcircle_id)

    print(city_district)
    print(city_bizcircle)
    print(test)