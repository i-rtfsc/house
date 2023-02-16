declare -a districts=("pudong" "minhang" "baoshan" "songjiang" "jiading" "qingpu")
for district in "${districts[@]}"
do
    echo "$district"
    # sf1a3a4a5p3
    # 限制只看普通住宅、70-130㎡、300-400W
    scrapy crawl lianjia --nolog -a city=sh -a type=ershoufang -a district=$district -a restrict=sf1a3a4a5p3
done
