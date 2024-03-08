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

import optparse
import os
import subprocess
import threading
import time

import schedule

from excel import db2xl

city = "sh"
type = "ershoufang"
districts = ["pudong", "minhang", "baoshan", "songjiang", "jiading", "qingpu"]
restrict = "sf1a3a4a5p3"
auto = 1
email = "anqi.huang@outlook.com"


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

    # email
    option.add_option("-e", "--email", dest="email", type="string",
                      help="email", default="anqi.huang@outlook.com")

    parser.add_option_group(option)
    (options, args) = parser.parse_args()

    return (options, args)


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def do_scrapy(city, type, district, restrict):
    os.system(
        "scrapy crawl lianjia --nolog -a city={} -a type={} -a district={} -a restrict={}".format(city, type, district,
                                                                                                  restrict))


def compress_file():
    pwd = os.getcwd()
    data_dir = os.path.join(pwd, "data")

    if restrict:
        name = "{}-{}-lianjia".format(city, restrict)
    else:
        name = "{}-lianjia".format(city)

    db_name = name + ".db"
    gz_name = name + ".tar.gz."

    cmd = "tar -cvzf - {db_name} | split -b 10M -d -a 3 - {gz_name}".format(db_name=db_name,
                                                                            gz_name=gz_name)
    os.chdir(data_dir)
    os.system(cmd)
    os.system("rm -rf {}".format(db_name))
    os.chdir(pwd)


def decompress_file():
    pwd = os.getcwd()
    data_dir = os.path.join(pwd, "data")

    if restrict:
        name = "{}-{}-lianjia".format(city, restrict)
    else:
        name = "{}-lianjia".format(city)

    gz_name = name + ".tar.gz.*"
    file = os.path.join(data_dir, gz_name)
    cmd = "cat {file} | tar -xvzf - -C {data_dir}".format(file=file, data_dir=data_dir)
    os.chdir(data_dir)
    os.system(cmd)
    os.system("rm -rf {}".format(gz_name))
    os.chdir(pwd)


def upload():
    os.system("sleep 2")
    cmd = "git config user.email"
    ret, output = subprocess.getstatusoutput(cmd)
    if ret == 0:
        if email == output:
            cmd = "git add ."
            ret, output = subprocess.getstatusoutput(cmd)
            if ret != 0:
                print("git add fail:\n %s" % (output))

            cmd = "git commit -m \"Update datas via upload\""
            ret, output = subprocess.getstatusoutput(cmd)
            if ret != 0:
                print("git commit fail:\n %s" % (output))

            cmd = "git push -u origin HEAD:main"
            ret, output = subprocess.getstatusoutput(cmd)
            if ret != 0:
                print("git push fail:\n %s" % (output))
            else:
                print("git push success!")


def do_job():
    decompress_file()
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

    compress_file()
    upload()


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

    global email
    email = options.email.strip()

    auto = 1
    schedule_time = []
    for i in options.schedule.split("/"):
        schedule_time.append(i)

    if len(schedule_time) == 1 and schedule_time[0] == "0":
        auto = 0

    print('main func, city =', city, ', type =', type, ', districts =', districts, ', restrict =', restrict,
          ', email =', email, ', auto =', auto, ', schedule time =', schedule_time)

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
