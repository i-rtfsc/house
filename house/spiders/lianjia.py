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
import re
from datetime import datetime

import scrapy
from scrapy import Selector
from scrapy.http.response.text import TextResponse

from house.items import HouseItem


class Lianjia(scrapy.Spider):
    name = 'lianjia'
    DEBUG = True
    DEBUG_DATA = False
    # 打开后，只爬两页数据，所有提交之前一定不要打开。
    DEBUG_PAGE = False

    def __init__(self, **kwargs):
        super().__init__(name=None, **kwargs)

        self.count = dict()

        # 城市
        self.city = getattr(self, 'city', None)
        if self.city is None:
            setattr(self, 'city', 'sh')
            self.city = 'sh'

        # 类型
        # ershoufang 二手房
        # xiaoqu 小区 (如果是查询小区，会有二手房、chengjiao 成交[需要登陆])
        # luopan
        self.type = getattr(self, 'type', None)
        if self.type is None:
            setattr(self, 'type', 'ershoufang')
            self.type = 'ershoufang'

        # 区
        self.district = getattr(self, 'district', None)
        if self.district is None:
            setattr(self, 'district', 'songjiang')
            self.district = 'songjiang'

        # 限制条件
        # sf系列为用途，如
        #   sf1 : 普通住宅
        # p系列为售价，如
        #   p3  : 300-400W
        # a系列为面积，如
        #   a3  : 70-90㎡
        #   a4  : 90-110㎡
        #   a5  : 110-130㎡
        # 连在一起的顺序请自行查看链家网
        # sf1a3a4a5p3
        self.restrict = getattr(self, 'restrict', None)
        if self.restrict == "null" or self.restrict == "None":
            self.restrict = None

        self.base_url = "https://{}.lianjia.com".format(self.city)

    def start_requests(self):
        if self.restrict:
            url = "https://{}.lianjia.com/{}/{}/{}".format(self.city, self.type, self.district, self.restrict)
        else:
            url = "https://{}.lianjia.com/{}/{}".format(self.city, self.type, self.district)
        print("start requests, url = ", url)
        if self.type == "ershoufang":
            yield scrapy.Request(url, self.parse_district)
        # elif self.type == "xiaoqu":
        #     # 通过小区的方式获取层级比较深
        #     # 而且数据可能没有，甚至没有数据时显示别的小区数据
        #     # 所以不推荐使用
        #     yield scrapy.Request(url, self.parse_trading_area_links)
        else:
            print(self.type)

        # 链家限制只能查100页，但为了严谨一点，在第一页查到总共有多少页会更好。
        # for page in range(1, 101):
        #     url = "https://{}.lianjia.com/{}/{}/pg{}/".format(self.city, self.type, self.district, self.page)
        #     print(url)
        #     yield scrapy.Request(url, self.parse_house_list, cb_kwargs=dict(page=page))

    def parse_data(self, text):
        start_index = text.find('</span>') + len('</span>')
        end_index = text.find('</li>', start_index)
        return text[start_index:end_index].strip()

    def parse_district(self, response: TextResponse):
        """解析区总页码"""
        sel = Selector(response)

        # 链接分页
        page_data = sel.css(".house-lst-page-box::attr(page-data)").extract_first()
        page_data = json.loads(page_data)

        if page_data['totalPage'] >= 1:
            # 直接用第一页的数据：
            # 1. 直接调parse_house_list会有问题
            # 2. 再写一次parse_house_list里的代码又很麻烦
            # 所以就索性再爬一次第一页，反正也就只有第一页多爬一次而已
            if self.DEBUG_PAGE:
                total_page = 2
            else:
                total_page = page_data['totalPage'] + 1
            for page in range(1, total_page):
                if self.restrict:
                    url = "https://{}.lianjia.com/{}/{}/pg{}{}/".format(self.city, self.type, self.district, page,
                                                                        self.restrict)
                else:
                    url = "https://{}.lianjia.com/{}/{}/pg{}/".format(self.city, self.type, self.district, page)

                print("parse district url = ", url)
                yield scrapy.Request(url, self.parse_house_list, cb_kwargs=dict(page=page))

    def parse_house_list(self, response: TextResponse, page):
        """根据区页，解析到每一个房子到链接"""
        sel = Selector(response)
        lis = sel.css('ul.sellListContent li')

        total = "total_{}".format(page)
        current = "current_{}".format(page)
        self.count[total] = len(lis)
        self.count[current] = 0

        for li in lis:
            # title = li.css('div.title a::text').get().replace('：', '').replace(',', ' ').replace("\n", '')
            link = li.css("div[class='title'] a::attr(href)").extract()[0]
            self.count[current] = self.count[current] + 1
            yield scrapy.Request(url=link, callback=self.parse_house_detail,
                                 cb_kwargs=dict(page=page, total_count=self.count[total],
                                                current_count=self.count[current]))

    def parse_house_detail(self, response: TextResponse, page, total_count, current_count):
        """解析房子"""
        if self.DEBUG:
            print("page = {} , count = {}/{} ".format(page, current_count, total_count))

        sel = Selector(response)

        house = HouseItem()

        # 第几页
        house['page'] = page
        # 当前页的总数
        house['total_count'] = total_count
        # 当前页的第几个
        house['current_count'] = current_count

        # 房屋ID
        house['house_id'] = response.url.split("/")[-1].replace(".html", "")
        # 房屋url
        house['house_url'] = response.url

        # 标题
        house['title'] = sel.css('.title-wrapper .title .main::text').extract_first()
        # 总价
        house['total_price'] = float(sel.css('.overview .content .price .total::text').extract_first())
        # 单价
        house['unit_price'] = int(sel.css('.overview .content .unitPrice .unitPriceValue::text').extract_first())

        location_info = sel.css('.overview .content .aroundInfo .areaName .info').extract_first()
        location_info_list = []
        for split1 in location_info.split(">"):
            for split2 in split1.split("<"):
                split2 = split2.strip()
                save = False
                if "/" in split2 or "\"" in split2 or len(split2) == 0:
                    save = False
                else:
                    save = True

                if save:
                    location_info_list.append(split2)

        house['district'] = location_info_list[0]
        house['bizcircle'] = location_info_list[1]

        # 小区
        house['xiaoqu'] = sel.css('.overview .content .aroundInfo .communityName a.info::text').extract_first()

        # 小区ID
        house['xiaoqu_id'] = sel.css(
            '.overview .content .aroundInfo .communityName a.info::attr(href)').extract_first().replace('/xiaoqu/',
                                                                                                        '').replace('/',
                                                                                                                    '')
        # 房屋户型
        # house['layout'] = sel.css('#introduction .base .content ul li:nth-child(1)::text').extract_first()
        house['layout'] = self.parse_data(
            sel.css('.m-content .box-l .base .content ul li:nth-child(1)').extract_first())
        if self.DEBUG_DATA:
            print("layout = {}".format(house['layout']))

        # 所在楼层
        # house['flood'] = sel.css('#introduction .base .content ul li:nth-child(2)::text').extract_first()
        house['flood'] = self.parse_data(sel.css('.m-content .box-l .base .content ul li:nth-child(2)').extract_first())
        if self.DEBUG_DATA:
            print("flood = {}".format(house['flood']))

        # 建筑面积
        # building_area = sel.css('#introduction .base .content ul li:nth-child(3)::text').extract_first()
        building_area = self.parse_data(sel.css('.m-content .box-l .base .content ul li:nth-child(3)').extract_first())
        if self.DEBUG_DATA:
            print("building_area = {}".format(building_area))

        house['_building_area'] = building_area
        house['building_area'] = float(building_area.replace("㎡", ""))

        # 建造时间
        house['building_year'] = int(
            re.findall(r'\d+', sel.css("div[class='subInfo noHidden']::text").extract_first())[0])

        # 户型结构
        house['structure'] = sel.css('#introduction .base .content ul li:nth-child(4)::text').extract_first()
        # 套内面积
        house['house_area'] = sel.css('#introduction .base .content ul li:nth-child(5)::text').extract_first()
        # 建筑类型
        house['building_type'] = sel.css('#introduction .base .content ul li:nth-child(6)::text').extract_first()
        # 房屋朝向
        house['orientation'] = sel.css('#introduction .base .content ul li:nth-child(7)::text').extract_first()
        # 建筑结构
        house['building_structure'] = sel.css('#introduction .base .content ul li:nth-child(8)::text').extract_first()
        # 装修情况
        house['decoration'] = sel.css('#introduction .base .content ul li:nth-child(9)::text').extract_first()
        # 梯户比例
        house['house_elevator'] = sel.css('#introduction .base .content ul li:nth-child(10)::text').extract_first()
        # 配备电梯
        house['elevator'] = sel.css('#introduction .base .content ul li:nth-child(11)::text').extract_first()
        # item['产权年限'] = sel.css('#introduction .base .content ul li:nth-child(12)::text').extract_first()

        # 挂牌时间
        house['listing_time'] = sel.css(
            '#introduction .transaction .content ul li:nth-child(1) span:nth-child(2)::text').extract_first()
        # 交易权属
        house['house_characteristics'] = sel.css(
            '#introduction .transaction .content ul li:nth-child(2) span:nth-child(2)::text').extract_first()
        # 上次交易
        house['last_deal'] = sel.css(
            '#introduction .transaction .content ul li:nth-child(3) span:nth-child(2)::text').extract_first()
        # 房屋用途
        house['land_usage'] = sel.css(
            '#introduction .transaction .content ul li:nth-child(4) span:nth-child(2)::text').extract_first()
        # 房屋年限
        house['deal_year'] = sel.css(
            '#introduction .transaction .content ul li:nth-child(5) span:nth-child(2)::text').extract_first()
        # 产权所属
        house['ownership'] = sel.css(
            '#introduction .transaction .content ul li:nth-child(6) span:nth-child(2)::text').extract_first()
        # 抵押信息
        house['mortgage'] = sel.css(
            '#introduction .transaction .content ul li:nth-child(7) span:nth-child(2)::attr(title)').extract_first()
        # 房本备件
        house['annex'] = sel.css(
            '#introduction .transaction .content ul li:nth-child(8) span:nth-child(2)::text').extract_first()
        # 关注人数(多少人关注)
        house['follow_number'] = int(sel.css('#favCount::text').extract_first())
        # 看房人数(多少人看过)
        house['look_number'] = int(sel.css('#cartCount::text').extract_first())
        # 爬数据时间
        house['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        yield house

    def parse_trading_area_links(self, response):
        """提取商圈链接"""
        # 松江新城
        # 洞泾
        # 佘山
        # ...

        sel = Selector(response)
        links = sel.css("div[data-role='ershoufang'] div:nth-child(2) a::attr(href)").extract()
        for link in links:
            url = self.base_url + link
            print("parse trading area url = ", url)
            yield scrapy.Request(url=url, callback=self.parse_village_list, cb_kwargs=dict(page=1))

    def parse_village_list(self, response, page):
        """提取小区链接"""
        sel = Selector(response)
        links = sel.css(".listContent .xiaoquListItem .img::attr(href)").extract()
        for link in links:
            village_id = link.split("/")[-2]
            print("parse village url = ", link)
            # 小区房源 https://sh.lianjia.com/ershoufang/5011000000891/
            url = self.base_url + "/ershoufang/" + village_id + "/"
            yield scrapy.Request(url=url, callback=self.parse_house_list, cb_kwargs=dict(page=page))
            # 成交房源(需要登陆)
            # url = self.base_url + "/chengjiao/" + village_id + "/"
            # yield scrapy.Request(url=url, callback=self.parse_house_list, cb_kwargs=dict(page=page))

        # 翻页获取小区链接
        page_data = sel.css(".house-lst-page-box::attr(page-data)").extract_first()
        page_data = json.loads(page_data)
        if self.DEBUG:
            print("page = {}/{}".format(page_data['curPage'], page_data['totalPage']))

        if int(page_data['curPage']) < int(page_data['totalPage']):
            url = response.meta["ref"] + 'pg' + str(page_data['curPage'] + 1)
            # print('翻页获取小区链接 = ', url)
            yield scrapy.Request(url=url, callback=self.parse_village_list, cb_kwargs=dict(page=page_data['curPage']))
