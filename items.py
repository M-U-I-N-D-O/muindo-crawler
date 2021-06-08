import requests
from bs4 import BeautifulSoup
from azure.storage.blob import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from azure.core.exceptions import ResourceExistsError
from utils import colors
from models import *
from sqlalchemy.exc import *

engine = create_engine('mysql://admin:tnfkadlek1@myfirstdb.cwtu7qrvwhdo.ap-northeast-2.rds.amazonaws.com:3306/muindo?charset=utf8mb4')
Session = sessionmaker(bind=engine)
session = Session()

#신발, 아우터, 원피스, 바지, 상의, 스커트

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
}


def get_crawling_text(response):
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def get_category_colors(category_id: str) -> dict:
    url = 'https://search.musinsa.com/category/' + category_id
    response = requests.get(url=url, headers=headers)

    color_info = {}

    if response.status_code == 200:
        soup = get_crawling_text(response)
        colors = soup.select('#toolTip > li > a')
        for color in colors:
            color_info[color['alt']] = color['data-code']

    return color_info


def get_item_info(category, color, page):

    url = 'https://search.musinsa.com/category/' + category + '?page=' + str(page) + '&color=' + color
    response = requests.get(url=url, headers=headers)

    item_info_urls = {}

    if response.status_code == 200:
        soup = get_crawling_text(response)
        items = soup.select('#searchList > li > div.li_inner > div.list_img > a')
        prices = soup.select('#searchList > li > div.li_inner > div.article_info > p.price')
        item_price = list(zip(items, prices))
        length = 20 if len(item_price) >= 20 else len(item_price)
        for item, p in item_price[:length]:
            price = p.text.strip()
            item_info_urls[item['href']] = int(price.split(' ')[-1][:-1].replace(',', ''))

    return item_info_urls


def upload_azure_blob(url, image_name):

    response = requests.get('https:' + url)
    isduplicate = False

    if response.status_code == 200:
        data = response.content
        blob = BlobClient.from_connection_string(conn_str='DefaultEndpointsProtocol=https;AccountName=sherlockodds;AccountKey=RIlkLeL57ZPdy3umfCGh6UjQIcdm7bRs3buFNrKiCOLlynk7T/ljVwVJI+RFZQtkW9GrAlx0zbrJfylATzS1fg==;EndpointSuffix=core.windows.net',
                                                 container_name='musinsa',
                                                 blob_name=image_name)
        try:
            blob.upload_blob(data)

        except ResourceExistsError:
            isduplicate = not isduplicate
            pass

    return isduplicate, blob.url

def get_item_details(url, item=None):

    response = requests.get(url=url, headers=headers)

    if response.status_code == 200:
        soup = get_crawling_text(response)
        category = soup.select_one('#page_product_detail > div.right_area.page_detail_product > div.right_contents.section_product_summary > div.product_info > p > a:nth-child(1)')
        category = category['href'].split('/')[-1]
        sub_category = soup.select_one('#page_product_detail > div.right_area.page_detail_product > div.right_contents.section_product_summary > div.product_info > p > a:nth-child(2)')
        sub_category = sub_category['href'].split('/')[-1]
        name = soup.select_one('#page_product_detail > div.right_area.page_detail_product > div.right_contents.section_product_summary > span > em')
        itemno = soup.select_one('#product_order_info > div.explan_product.product_info_section > ul > li:nth-child(1) > p.product_article_contents > strong')
        print(itemno.text)
        itemno = itemno.text.split(' / ')
        brand = itemno[0]
        itemno = ''.join(itemno[1:])
        img_url = soup.select_one('#bigimg')
        img_url = img_url['src']
        isduplicate, new_url = upload_azure_blob(img_url, brand+'_'+img_url.split('/')[-1])

        if isduplicate:

            print('already exists'+' '+item.musinsa)

            try:
                existing_item = session.query(Item).filter(Item.url== new_url).one()
            except:
                return isduplicate

            if existing_item.category.find(category) == -1:
                existing_item.category += ' | ' + category

            if existing_item.subcategory.find(sub_category) == -1:
                existing_item.subcategory += ' | ' + sub_category

            return isduplicate

        item.url = new_url

        if item.category.find(category) == -1:
            item.category += ' | '+category

        item.brand = brand
        item.itemno = itemno

        if item.subcategory and item.subcategory.find(sub_category) == -1:
            item.subcategory += ' | ' + sub_category
        else:
            item.subcategory = sub_category

        item.name = (name.text)


    return item


def get_total_pages(c, v):

    url = 'https://search.musinsa.com/category/'+c+'?color='+v
    response = requests.get(url=url, headers=headers)

    if response.status_code == 200:
        soup = get_crawling_text(response)
        total_pages = soup.select_one('#goods_list > div.boxed-list-wrapper > div.thumbType_box.box > span.pagingNumber > span.totalPagingNum')

        if total_pages is None:
            return 0

        return int(total_pages.text)
#'004', '054', '020', '002', '009',
category_ids = [ '007', '003', '022', '018', '005']


for category in category_ids:

    for name, id in colors.items():
        total_pages = get_total_pages(category, id)

        if not total_pages : continue

        total_pages = min(total_pages, 1)

        for page in range(1, total_pages+1):
            item_urls = get_item_info(category, id, page)
            items = []

            for url, price in item_urls.items():
                item = Item()
                item.musinsa = url
                item.price = price
                item.color = id
                item.category = category
                item.updated = datetime.now()

                if get_item_details(url,item) == True:
                    continue

                print(item.category, item.name, item.url)
                items.append(item)

            session.add_all(items)
            session.commit()


