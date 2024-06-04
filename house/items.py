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

import scrapy


class HouseItem(scrapy.Item):
    # 房屋ID
    house_id = scrapy.Field()
    # 房屋url
    house_url = scrapy.Field()
    # 标题
    title = scrapy.Field()
    # 总价
    total_price = scrapy.Field()
    # 单价
    unit_price = scrapy.Field()
    # 区域
    # 如：松江
    district = scrapy.Field()
    # 区域ID
    # district_id = scrapy.Field()
    # 商圈
    # 如：泗泾
    # lianjia就是这么起的英文的，虽然觉得trading area更合适
    # 但对于中国人来说，他这个叫法更能让人理解
    bizcircle = scrapy.Field()
    # 商圈ID
    # bizcircle_id = scrapy.Field()

    # 小区
    xiaoqu = scrapy.Field()
    # 小区ID
    xiaoqu_id = scrapy.Field()

    # TODO
    # 房间数
    room = scrapy.Field()
    # 房屋户型
    layout = scrapy.Field()
    # 所在楼层
    flood = scrapy.Field()
    # 建筑面积
    _building_area = scrapy.Field()
    building_area = scrapy.Field()
    # 建造时间
    building_year = scrapy.Field()
    # 户型结构
    structure = scrapy.Field()
    # 套内面积
    house_area = scrapy.Field()
    # 建筑类型
    building_type = scrapy.Field()
    # 房屋朝向
    orientation = scrapy.Field()
    # 建筑结构
    building_structure = scrapy.Field()
    # 装修情况
    decoration = scrapy.Field()
    # 梯户比例
    house_elevator = scrapy.Field()
    # 配备电梯
    elevator = scrapy.Field()

    # 挂牌时间
    listing_time = scrapy.Field()
    # 交易权属
    house_characteristics = scrapy.Field()
    # 上次交易
    last_deal = scrapy.Field()
    # 房屋用途
    land_usage = scrapy.Field()
    # 房屋交易年限
    deal_year = scrapy.Field()
    # 产权所属
    ownership = scrapy.Field()
    # 抵押信息
    mortgage = scrapy.Field()
    # 房本备件
    annex = scrapy.Field()
    # 关注人数
    follow_number = scrapy.Field()
    # 看房人数(多少人看过)
    look_number = scrapy.Field()
    # (第一次)爬数据时间
    crawl_time = scrapy.Field()
    # 爬数据时间
    update_time = scrapy.Field()

    # 第几页
    page = scrapy.Field()
    # 当前页的总数
    total_count = scrapy.Field()
    # 当前页的第几个
    current_count = scrapy.Field()
