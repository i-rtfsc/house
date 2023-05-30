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
import optparse
import threading
import time

import schedule

from excel import db2xl

city = "sh"
type = "ershoufang"
districts = ["pudong", "minhang", "baoshan", "songjiang", "jiading", "qingpu"]
restrict = "sf1a3a4a5p3"
auto = 1

def parseargs():
    usage = "usage: %prog [options] arg1 arg2"
    parser = optparse.OptionParser(usage=usage)

    option = optparse.OptionGroup(parser, "house scrapy crawl options")

    # 城市
    option.add_option("-c", "--city", dest="city", type="string",
                      help="which city", default="sh")
    # 类型：二手房
    option.add_option("-t", "--type", dest="type", type="string",
                      help="ershoufang/loupan/chengjiao", default="ershoufang")
    # 区域，如有多个则以/隔开
    option.add_option("-d", "--districts", dest="districts", type="string",
                      help="city districts", default="pudong/minhang/baoshan/songjiang/jiading/qingpu")
    # 限制条件
    option.add_option("-r", "--restrict", dest="restrict", type="string",
                      help="restrict", default="sf1a3a4a5p3")

    option.add_option("-s", "--schedule", dest="schedule", type="string",
                      help="schedule", default="12:00/17:30")

    parser.add_option_group(option)
    (options, args) = parser.parse_args()

    return (options, args)


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def do_scrapy(city, type, district, restrict):
    os.system("scrapy crawl lianjia --nolog -a city={} -a type={} -a district={} -a restrict={}".format(city, type, district, restrict))


def do_job():
    for district in districts:
        # from concurrent.futures import ProcessPoolExecutor, wait, ALL_COMPLETED
        # process_pool = ProcessPoolExecutor()
        # feature = process_pool.submit(do_scrapy, city, type, district, restrict)
        # wait([feature], return_when=ALL_COMPLETED)
        # result = feature.result()
        # process_pool.shutdown()
        do_scrapy(city, type, district, restrict)

    # 转存到 excel
    if restrict:
        db2xl.save(districts, "{}-{}-lianjia".format(city, restrict))
    else:
        db2xl.save(districts, "{}-lianjia".format(city))


def main():
    (options, args) = parseargs()

    global city
    city = options.city.strip()

    global type
    type = options.type.strip()

    global districts
    district = options.districts.strip()
    districts = district.split("/")

    global restrict
    restrict = options.restrict.strip()
    if restrict == "null":
        restrict = None

    auto = 1
    global schedule
    schedule = options.schedule
    schedule_time = schedule.split("/")
    if len(schedule_time) == 1 and schedule_time[0] == "0":
        auto = 0

    print('main func, city =', city, ', type =', type, ', districts =', districts, ', restrict =', restrict,
          ', auto =', auto, ', schedule time =', schedule_time)

    if auto:
        for i in schedule_time:
            schedule.every().day.at(i).do(run_threaded, do_job)
        while True:
            schedule.run_pending()
            time.sleep(5)
    else:
        # 不是自动则不启动schedule，仅仅执行一次
        do_job()


if __name__ == "__main__":
    main()
