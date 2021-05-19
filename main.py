from bs4 import BeautifulSoup
import requests
from azure.storage.blob import *
import os

def get_musinsa_item_images(url: str) -> None:

    response = requests.get(url)


    if response.status_code == 200:

        data = response.content
        blob = BlobClient.from_connection_string(conn_str=os.environ.get('AZURE_STORAGE_CONNECTION_STRING'),
                                                 container_name='musinsa',
                                                 blob_name='musinsa_image.jpg')

        # blob.upload_blob(data)

        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        li = soup.select("#searchList > li:nth-child(1)")

        for i in li:
            print(i)

url = 'https://search.musinsa.com/category/001001?device=&d_cat_cd=001001&brand=&rate=&page_kind=search&list_kind=small&sort=pop&sub_sort=&page=1&display_cnt=90&sale_goods=&ex_soldout=&color=3&price1=&price2=&exclusive_yn=&size=&tags=&sale_campaign_yn=&timesale_yn=&q='
get_musinsa_item_images(url)






