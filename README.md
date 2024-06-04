# 重要

main分支包含作者每天爬数据的记录，导致整个代码代码仓非常大，如：![GitHub repo size](https://img.shields.io/github/repo-size/i-rtfsc/house)

建议你拉代码时只单独拉 release 分支，命令如下：

```bash
git clone --single-branch --branch release https://github.com/i-rtfsc/house.git
```

# 非常重要

如果发现爬不了数据，请直接在根目录执行以下命令，根据log进行修改。
2024年之前这个网站不做任何限制，直接可以爬数据。
- 2024年4月份  新增了 robots.txt 规则
- 2024年6月1号 新增了检测脚本爬虫规则，必须配置 USER_AGENT 伪造浏览器才行

```bash
scrapy crawl lianjia
```

# 背景
最近(2023年初)想在上海买房，天天被各种公众号、大V、中介贩卖焦虑：现在是最好的买房时期，过了这一波就要涨价了。

本人又是小白，对很多信息都没有自己的判断，经常看网上各种数据分析的头头是道，本着怀疑的精神去研究这些数据的来源。想到了自己把原始数据爬下来，就可以印证别人说的到底是真话还是假话了。

# 能力
- 链家二手房数据
- 全国所有房源
- 自定义筛选条件
- 存储到数据库、Excel

# 关键数据
- 房屋ID
- 区域
- 商圈
- 小区
- 标题
- 总价
- 单价
- 涨(降)幅度
- 价格走势
- 房屋户型
- 所在楼层
- 建筑面积
- 年代
- 朝向
- 装修
- 梯户比例
- 配备电梯
- 挂牌时间
- 上次交易
- 房屋交易年限
- 交易权属
- 房屋用途
- 关注人数
- 带看人数
- 房屋url
- ...

# 使用说明

## 环境
pip install -r requirements.txt

## city.py
这个脚本是用来获取全国任意一个城市的id、区名、商圈名等等。对后面的爬虫选择的限制条件很重要。
当然，如果比较熟悉链家的二手房网站，也可以通过网页地址得出城市的id、区名、商圈名等等。

## main.py
这个脚本是用来执行scrapy crawl命令进行爬虫，可以添加的限制条件有：
- city：爬哪个城市的数据、比如上海就是sh，深圳就是zs。
> 默认是上海。

- type: 爬数据的类型，如二手房就是：ershoufang；当时考虑加上成交、新楼盘等，目前因为成交数据需要登录账号，暂时搁浅了。 
> 默认是二手房。

- district：哪个区，选择多个或者一个。
> 默认是浦东、闵行、宝山、松江、嘉定、青浦。
> 输入时请有/分割开，如：pudong/minhang/baoshan/songjiang/jiading/qingpu
> 默认是pudong/minhang/baoshan/songjiang/jiading/qingpu

- restrict：更详细的限制条件，如：限制只看普通住宅、70-130㎡、300-400W，对应的字符串就是：sf1a3a4a5p3
> 限制条件对应的字符串可以通过打开链家网站，选择到某个具体的限制条件后，根据网页地址的变化就知道了。
> 如 https://sh.lianjia.com/ershoufang/songjiang/pg2sf1a3a4a5p3/
> 默认是sf1a3a4a5p3，如果不限制需要输入null。

- schedule: 脚本是每天定时执行的时间。
> 如果输入0，则只执行一次。
> 输入时请有/分割开。
> 默认是12:00/17:30，也就是每天中午12点，下午5点半执行。 

如果你的需求跟我一样，直接执行：python main.py

执行完成之后会保存到db文件中，db文件的命名规则：city-restrict-lianjia.db，例如本案例就就是：sh-sf1a3a4a5p3-lianjia.db

数据库会根据每个区新建一个table，如果你想知道某个房源的变化，可以每天都爬一次，数据库中的price_trend保存每次价格变化的时间和价格。

数据库每列对应的含义可以查看items.py里的备注。

> python main.py -d pudong/minhang/baoshan/xuhui/putuo/yangpu/changning/songjiang/jiading/huangpu/jingan/hongkou/qingpu/fengxian/jinshan/chongming -s 20:00 -r null

## excel
爬下来的原始数据保存在db中，不是很方便查阅。爬完之后可以通过db2xl.py脚本转存到excel文件中。

excel的每个sheet页还是按区来命名，其中标红的行是涨价、标绿的行是降价。

从这里就可以大概知道总体是涨了还是降了。

注意，这里只是简单的标注一下涨(降)幅度情况，不此工程不做任何数据分析。

## check_exists.py
每次爬的数据都是增量更新的，但有一部分房源（非成交）的链接失效(猜测可能是房东主动下架...)。

check_exists脚本会检测网页是否404，来决定是否要删除相关的数据。


# 备注
数据不会骗人，数据分析会！

有会数据分析的大佬，可以交流交流。

最后希望这个工程对你有帮助，买到心仪的房子。
