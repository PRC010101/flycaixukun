# -*- coding: utf-8 -*-
import requests
from lxml import etree
import wx
import time
import csv
import pandas as pd
from matplotlib import pyplot
import re

def get_content(url):
    product_dict = {}
    html = requests.get(url, headers=headers)
    selector = etree.HTML(html.text)
    product_infos = selector.xpath('//ul[@class="parameter2 p-parameter-list"]')
    product_brand = selector.xpath('//*[@id="parameter-brand"]/li/@title')
    product_dict['brand'] = product_brand[0]
    for product in product_infos:
        product_name = product.xpath('li[1]/@title')[0]
        product_number = product.xpath('li[2]/@title')[0]
        product_price = get_product_price(product_number)
        product_good = get_product_comment(product_number)
        product_words = get_product_rank(product_number)
        product_dict['name'] = product_name
        product_dict['price'] = product_price
        product_dict['number'] = product_number
        product_dict['good'] = product_good['GoodCount']
        product_dict['general'] = product_good['GeneralCount']
        product_dict['bad'] = product_good['PoorCount']
        product_dict['rank'] = product_words
    print(product_dict)
    result = product_dict['brand']+ ','+product_dict['name']+','+str(product_dict['price'])+','+str(product_dict['good'])+','+str(product_dict['general'])+','+str(product_dict['bad'])+','+str(product_dict['rank'])
    if type(result.split(',')).__name__ == "list":
        return result.split(',')
    else:
        pass


def get_product_price(skuid):  # 获得价格
    url = 'https://p.3.cn/prices/mgets?&skuIds=J_{}'.format(str(skuid))
    html = requests.get(url, headers=headers).json()
    return html[0].get('p')


def get_product_comment(skuid):  # 获得好评、差评数
    url = 'https://club.jd.com/comment/productCommentSummaries.action?referenceIds={}'.format(str(skuid))
    html = requests.get(url, headers=headers).json()
    html = html['CommentsCount']
    ml =html[0]
    return ml


def get_product_rank(skuid):  #获得排名
    url = 'https://c0.3.cn/race/price/rank?&sku={}'.format(str(skuid))
    html = requests.get(url, headers=headers).json()
    mk = html['msg']
    if mk == 'ok':
        return html['data']['rank']
    else:
        html = '999999'
        return html


def get_alldata_csv():
    urls = [
        'https://list.jd.com/list.html?cat=9987,653,655&page={}&sort=sort_rank_asc&trans=1&JL=6_0_0&ms=10#J_main'.format(
            str(i)) for i in range(1, 10)]
    path = 'result_' + str(
        time.strftime('%Y{y}%m{m}%d{d}%H{h}%M{f}%S{s}').format(y='年', m='月', d='日', h='时', f='分', s='秒')) + '.csv'
    with open(path, 'a', newline='', encoding='gbk') as f:  # 写入字段头
        write = csv.writer(f, dialect='excel')
        write.writerow(['品牌', '名称', '价格', '好评', '中评', '差评', '日销量排名'])
    for url in urls:
        html = requests.get(url, headers=headers)
        selector = etree.HTML(html.text)
        # 取到位置
        shop_list = selector.xpath('//ul[@class="gl-warp clearfix"]/li')
        list1 = []
        for shop in shop_list:
            shop_id = shop.xpath('div/@data-sku')[0]
            shop_url = 'https://item.jd.com/{}.html'.format(str(shop_id))
            result = get_content(shop_url)
            with open(path, 'a', newline='', encoding='gbk') as f:  # 写入采集结果
                write = csv.writer(f, dialect='excel')
                try:
                    write.writerow(result)
                except:
                    pass
    return path


def get_comment_picture(path,k):
    with open("{}".format(path), "r") as f:
        reader = csv.reader(f)
        rows = [row for row in reader]
    m = k
    xticks =['好评','中评','差评']
    list_1 = {rows[m][3],rows[m][4],rows[m][5]}
    pyplot.bar(range(5), [list_1.get(xtick, 0) for xtick in xticks], align='center')
    pyplot.xlabel("评论数目")
    pyplot.ylabel("评论类型")
    pyplot.title("该商品的好评、中评、差评情况")


if __name__ == '__main__':
    # 全局变量
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
    }
    path =get_alldata_csv()
    get_comment_picture(path, 2)


