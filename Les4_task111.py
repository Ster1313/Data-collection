from lxml import html
import requests
from datetime import datetime
from pymongo import MongoClient

client = MongoClient('localhost', 27017)

def mongodb_func():
    client = MongoClient('127.0.0.1', 27017)
    database = client['topnewsDB']
    return database

def paste_news_func(collection, news_data):
    if not collection.find_one(news_data):
        collection.insert_one(news_data)

def dom_func(link):
    response = requests.get(link, headers=header)
    return html.fromstring(response.text)

header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'}

def get_data_mailru(link):
    dom = dom_func(link)
    time_ = datetime.strptime(dom.xpath("//div[contains(@class, 'breadcrumbs')]//" + "span[contains(@class, 'js-ago')]/@datetime")[0],'%Y-%m-%dT%H:%M:%S%z')
    sourse_ = dom.xpath("//div[contains(@class, 'breadcrumbs')]//span[@class='link__text']/text()")[0]
    return time_, sourse_

def get_data_lentaru_func(link):
    dom = dom_func(link)
    time_ = datetime.strptime(dom.xpath("//div[@class='b-topic__info']/time/@datetime")[0], '%Y-%m-%dT%H:%M:%S%z')
    return time_

db = mongodb_func()

collection_lentaru = db.lentaru
collection_mailru = db.mailru
collection_yaru = db.yandexru

main_link_lenta_news = 'https://lenta.ru'
dom = dom_func(main_link_lenta_news)

lenta_news = dom.xpath("//time[@class='g-time']/../..")

for news in lenta_news:
    lenta_news_data = {}
    title = news.xpath(".//time[@class='g-time']/../text()")
    link = main_link_lenta_news + news.xpath(".//time[@class='g-time']/../@href")[0]
    sourse = "lenta.ru"
    time = get_data_lentaru_func(link)

    lenta_news_data['a_title'] = title[0].replace('\xa0', ' ')
    lenta_news_data['b_link'] = link
    lenta_news_data['c_source'] = sourse
    lenta_news_data['d_time'] = time
    paste_news_func(collection_lentaru, lenta_news_data)

main_link_mail_news = 'https://news.mail.ru/'
dom = dom_func(main_link_mail_news)

mail_news = dom.xpath("//span[@class='photo__caption']/..|// li[#class='list__item']/a")
for news in mail_news:
    mail_news_data = {}
    title = news.xpath(".//text()")[0].replace('\xa0', ' ')
    link = news.xpath(".//@href")[0]
    time, source = get_data_lentaru_func(link)

    mail_news_data['a_title'] = title
    mail_news_data['b_link'] = link
    mail_news_data['c_source'] = source
    mail_news_data['d_time'] = time

    paste_news_func(collection_mailru, mail_news_data)

main_link_yandex_news = 'https://yandex.ru/news'
dom = dom_func(main_link_yandex_news)

yandex_news = dom.xpath("//a[contains(@href, 'rubric=index') and @class='mg-card__link']/ ancestor::article")

for news in yandex_news:
    yandex_news_data = {}
    title = news.xpath(".//h2/text()")[0].replace('\xa0', ' ')
    link = news.xpath(".//a/@href")[0]
    source = news.xpath(".//span[@class='mg-card-source__source']//text()")[0]
    time = news.xpath(".//span[@class='mg-card-source__time']//text()")[0]

    yandex_news_data['a_title'] = title
    yandex_news_data['b_link'] = link
    yandex_news_data['c_source'] = source
    yandex_news_data['d_time'] = str(datetime.combine(datetime.today().date(), datetime.strptime(time, "%H:%M").time()))

    paste_news_func(collection_yaru, yandex_news_data)
