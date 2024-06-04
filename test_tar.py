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


def decompress_file(city, restrict=None):
    pwd = os.getcwd()
    data_dir = os.path.join(pwd, "data")

    if restrict:
        name = "{}-{}-lianjia".format(city, restrict)
    else:
        name = "{}-lianjia".format(city)

    gz_name = name + ".tar.gz"
    file = ""

    files = [f for f in os.listdir(data_dir) if f.startswith(gz_name)]
    files.sort()
    if files:
        for f in files:
            file += f + " "

    if file:
        os.chdir(data_dir)
        cmd = "cat {file} | tar -xvzf - -C {data_dir}".format(file=file, data_dir=data_dir)
        print("cmd = " + cmd)

        os.system(cmd)
        os.system("rm -rf {}".format(file))
        print("cmd = " + file)
        os.chdir(pwd)
        return True
    else:
        print("file does not exist")
        return False


def compress_file(city, restrict=None):
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


if __name__ == '__main__':
    decompress_file("sh")
    # compress_file("sh")
