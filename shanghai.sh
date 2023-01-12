# 浦东
# district = 'pudong'
# 闵行
# district = 'minhang'
# 宝山
# district = 'baoshan'
# 松江
# district = 'songjiang'
# 嘉定
# district = 'jiading'
# 青浦
# district = 'qingpu'
declare -a districts=("pudong" "minhang" "baoshan" "songjiang" "jiading" "qingpu")
for district in "${districts[@]}"
do
    echo "$district"
    # sf1a3a4a5p3
    # 限制只看普通住宅、70-130㎡、300-400W
    scrapy crawl lianjia --nolog -a city=sh -a type=ershoufang -a district=$district -a restrict=sf1a3a4a5p3
done
