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
from functools import partial

import schedule

import tar_file
from ding_ding import DingDing
from excel import db2xl


class Options(object):
    city = "sh"
    type = "ershoufang"
    districts = ["pudong", "minhang", "baoshan", "songjiang", "jiading", "qingpu"]
    restrict = "sf1a3a4a5p3"
    auto = 1
    email = "anqi.huang@outlook.com"
    token = None
    secret = None
    retry = 1
    RETRY_TIMES = 3


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
    # token
    option.add_option("-i", "--token", dest="token", type="string",
                      help="token", default=None)
    # secret
    option.add_option("-m", "--secret", dest="secret", type="string",
                      help="secret", default=None)

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


def upload(email):
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


def do_job(opt):
    print("\nstart do job, retry =", opt.retry)
    # 记录任务开始时间
    start_time = time.time()

    tar_file.decompress_file(os.path.dirname(os.path.abspath(__file__)),
                             opt.city, opt.restrict)
    for district in opt.districts:
        # from concurrent.futures import ProcessPoolExecutor, wait, ALL_COMPLETED
        # process_pool = ProcessPoolExecutor()
        # feature = process_pool.submit(do_scrapy, city, type, district, restrict)
        # wait([feature], return_when=ALL_COMPLETED)
        # result = feature.result()
        # process_pool.shutdown()
        do_scrapy(opt.city, opt.type, district, opt.restrict)

    # 转存到 excel
    msg = db2xl.save(opt.districts, opt.city, opt.restrict, 1)

    tar_file.compress_file(os.path.dirname(os.path.abspath(__file__)),
                           opt.city, opt.restrict)
    upload(opt.email)

    # 记录任务结束时间
    end_time = time.time()
    # 计算时间差
    duration_seconds = end_time - start_time
    if duration_seconds < 1800 and opt.retry < opt.RETRY_TIMES:
        opt.retry += 1
        do_job(opt)
    else:
        opt.retry = 1
        # 将时间差转换为时、分、秒的形式
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        msg += f"\n耗时: {int(hours)} 小时 {int(minutes)} 分 {int(seconds)} 秒"
        print(msg)
        if opt.token is None or opt.secret is None:
            print("token or secret not set...")
        else:
            im = DingDing(opt.token)
            im.set_secret(opt.secret)
            print(im.send_text(msg))


def main():
    opt = Options()

    (options, args) = parseargs()

    opt.city = options.city.strip()
    opt.type = options.type.strip()

    district = options.districts.strip()
    opt.districts = district.split("/")
    opt.restrict = options.restrict.strip()
    if opt.restrict == "null":
        opt.restrict = None

    opt.email = options.email.strip()

    auto = 1
    schedule_time = []
    for i in options.schedule.split("/"):
        schedule_time.append(i)

    if len(schedule_time) == 1 and schedule_time[0] == "0":
        auto = 0

    opt.token = options.token
    if not opt.token:
        opt.token = os.environ.get('GS_DD_TOKEN')

    opt.secret = options.secret
    if not opt.secret:
        opt.secret = os.environ.get('GS_DD_SECRET')

    print('main func, city =', opt.city, ', type =', opt.type, ', districts =', opt.districts, ', restrict =', opt.restrict,
          ', email =', opt.email, ', auto =', auto, ', schedule time =', schedule_time, ', token =', opt.token,
          ', secret =', opt.secret)

    if auto:
        for i in schedule_time:
            partial_job = partial(do_job, opt=opt)
            schedule.every().day.at(i).do(run_threaded, partial_job)
        while True:
            schedule.run_pending()
            time.sleep(5)
    else:
        # 不是自动则不启动schedule，仅仅执行一次
        do_job(opt)


if __name__ == "__main__":
    main()
