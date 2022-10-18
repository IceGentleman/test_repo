import csv
import os
import requests
import re
from lxml import etree
from fontTools.ttLib import TTFont

# 字体加密：字数爬取
'''
打开‘检查’，发现存在 𘜸𘜶𘜿𘜶𘜻 这样的字符，一般就是字体被加密了，打开‘查看网页源码’，搜索 font-face 或 font-family ，
该位置所在的标签包含了字体信息的些许描述； 另外𘜸𘜶𘜿𘜶𘜻 与类似 &#xe60d; 这样的字符相对应。
字体反反爬策略：
1、找到字体文件如 .ttf 或 .woff 文件（即数据包，通过字体转换在线工具即可查看）
2、下载该类型文件到本地
3、利用 fontTools 第三方库将字体文件转为 XML 格式
4、找到加密数据的映射关系：
    （1）只有单一的数字，可以直接观察得到
    （2）既有数字，又有其他字符，运用多个 for 循环替换得到
'''

# 字体解密
def Word_Count(html):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
    }
    woff_url = re.findall("format\(\'eot\'\); src: url\(\'(.*?)\'\) format\(\'woff\'\)", html)[0]
    print(woff_url)
    woff_content = requests.get(woff_url, headers=headers).content
    # 下载 woff 文件到本地
    with open('123.woff', 'wb') as fp:
        fp.write(woff_content)
    # 读取 woff 文件
    font_obj = TTFont('123.woff')
    # 将 woff 文件转为 xml 文件
    font_obj.saveXML('123.xml')
    cmap = font_obj.getBestCmap()
    print(cmap)
    dict_eng_int = {
        'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5', 'six': '6', 'seven': '7', 'eight': '8',
        'nine': '9', 'zero': '0', 'period': '.'
    }
    for i in cmap:
        for j in dict_eng_int:
            if cmap[i] == j:
                cmap[i] = dict_eng_int[j]
    print(cmap)
    # for key, value in cmap.items():
    #     key = hex(key)  # 10进制转16进制
    encrypted_data_list = re.findall('</style><span class=".*?">(.*?)</span>', html)
    encrypted_data_list2 = []
    for i in encrypted_data_list:
        encrypted_data_list3 = re.findall('\d+', i)
        encrypted_data_list2.append(encrypted_data_list3)
    for i in encrypted_data_list2:
        for j in enumerate(i):
            for k in cmap:
                if j[1] == str(k):
                    i[j[0]] = cmap[k]
    encrypted_data_list4 = []
    for i in encrypted_data_list2:
        encrypted_data_list4.append(''.join(i))
    print(encrypted_data_list4)
    return  encrypted_data_list4

# 常规数据爬取
def Book_Info(html):
    element = etree.HTML(html)
    li_list = element.xpath('//*[@id="book-img-text"]/ul/li')
    book_info_list = []
    for li in li_list:
        book_info = {}
        genre1 = li.xpath('./div[2]/p[1]/a[2]/text()')[0]
        genre2 = li.xpath('./div[2]/p[1]/i/text()')[0]
        genre3 = li.xpath('./div[2]/p[1]/a[3]/text()')[0]
        genre = genre3 + genre2 + genre1
        book_title = li.xpath('./div[2]/h2/a/text()')[0]
        book_link = 'https:' + li.xpath('./div[2]/h2/a/@href')[0]
        word_count = li.xpath('./div[2]/p[3]/span/span/text()')[0]
        author = li.xpath('./div[2]/p[1]/a[1]/text()')[0]
        summary = li.xpath('./div[2]/p[2]/text()')[0]
        # update_time = li.xpath('./td[6]/text()')[0]
        book_info['小说类型'] = genre
        book_info['小说书名'] = book_title
        book_info['小说链接'] = book_link
        book_info['小说作者'] = author
        book_info['小说简介'] = summary
        book_info_list.append(book_info)
    encrypted_data_list4 = Word_Count(html)
    for i in range(len(encrypted_data_list4)):
        book_info_list[i]['小说字数'] = encrypted_data_list4[i] + '万字'
    return book_info_list

# 数据保存为 csv 文件
def Writer(html):
    book_info_list = Book_Info(html)
    with open('起点小说.csv', 'w', encoding='utf-8-sig', newline='') as fp:
        fieldnames = ['小说类型', '小说书名', '小说链接', '小说作者', '小说简介', '小说字数']
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        if not os.path.getsize('起点小说.csv'):
            writer.writeheader()
        for book_info in book_info_list:
            writer.writerow(book_info)

if __name__ == '__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
    }
    for page in range(1, 4):
        if page == 1:
            url = 'https://www.qidian.com/all/chanId22/'
        else:
            url = f'https://www.qidian.com/all/chanId22-page{page}/'
        response = requests.get(url, headers=headers)
        html = response.text
        Writer(html)
        # print(book_info_list)
        # break
        print('爬取完毕！！！')






