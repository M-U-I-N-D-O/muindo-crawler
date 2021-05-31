import requests
from bs4 import BeautifulSoup
from models import *
from azure.storage.blob import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

engine = create_engine('mysql://admin:tnfkadlek1@myfirstdb.cwtu7qrvwhdo.ap-northeast-2.rds.amazonaws.com:3306/muindo?charset=utf8mb4')
Session = sessionmaker(bind=engine)
session = Session()

category_ids = ['005', '002', '020', '003', '001', '022']
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


def get_item_info(category, color, page=1):

    url = 'https://search.musinsa.com/category/' + category + '?page=' + str(page) + '&color=' + color
    response = requests.get(url=url, headers=headers)

    item_info_urls = []

    if response.status_code == 200:
        soup = get_crawling_text(response)
        items = soup.select('#searchList > li > div.li_inner > div.list_img > a')
        for item in items:
            item_info_urls.append(item['href'])

        total_pages = soup.select_one('#goods_list > div.boxed-list-wrapper > div.thumbType_box.box > span.pagingNumber > span.totalPagingNum')

        if page < 10 and page != int(total_pages.text):
            item_info_urls.extend(get_item_info(category=category, color=color, page = page + 1))

    return item_info_urls

def upload_azure_blob(url, image_name):

    response = requests.get('https:' + url)

    if response.status_code == 200:
        data = response.content
        blob = BlobClient.from_connection_string(conn_str='DefaultEndpointsProtocol=https;AccountName=sherlockodds;AccountKey=RIlkLeL57ZPdy3umfCGh6UjQIcdm7bRs3buFNrKiCOLlynk7T/ljVwVJI+RFZQtkW9GrAlx0zbrJfylATzS1fg==;EndpointSuffix=core.windows.net',
                                                 container_name='musinsa',
                                                 blob_name=image_name)
        # blob.upload_blob(data)

    return blob.url


def get_item_details(url, item=None):

    response = requests.get(url=url, headers=headers)

    if response.status_code == 200:
        soup = get_crawling_text(response)
        category = soup.select_one('#page_product_detail > div.right_area.page_detail_product > div.right_contents.section_product_summary > div.product_info > p > a:nth-child(1)')
        item.category = (category.text)
        sub_category = soup.select_one('#page_product_detail > div.right_area.page_detail_product > div.right_contents.section_product_summary > div.product_info > p > a:nth-child(2)')
        item.subcategory = (sub_category.text)
        name = soup.select_one('#page_product_detail > div.right_area.page_detail_product > div.right_contents.section_product_summary > span > em')
        item.name = (name.text)
        itemno = soup.select_one('#product_order_info > div.explan_product.product_info_section > ul > li:nth-child(1) > p.product_article_contents > strong')
        brand, itemno = itemno.text.split(' / ')
        item.brand = brand
        item.itemno = itemno
        price = soup.select_one('#goods_price')
        item.price = (price.text.strip())
        img_url = soup.select_one('#bigimg')
        img_url = img_url['src']
        new_url = upload_azure_blob(img_url, brand+'_'+img_url.split('/')[-1])
        item.url = new_url

    return item

# item = Item()
# item.color="test"
# item.musinsa="test"
#
# get_item_details('https://store.musinsa.com/app/goods/1964110', item)
#
# session.add(item)
# session.commit()

def run_crawling():

    for c in category_ids[:1]:
        colors = get_category_colors(c)

        for key, value in colors.items():
            item_info_urls = get_item_info(c, value)

            for item_url in item_info_urls:
                item = Item()
                item.color = key
                item.musinsa = item_url
                get_item_details(item_url, item)
                item.updated = datetime.now()
                print(item_url)
                #session.add(item)
            # session.commit()

run_crawling()

