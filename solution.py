import requests
from bs4 import BeautifulSoup
from models import *

def get_item_urls(url, gender, style):

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
    }
    cookies = {
        '_gf': gender
    }

    response = requests.get(url=url+'&style_type='+style, headers=headers, cookies=cookies)

    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        items = soup.select('body > div.wrap > div.right_area > form > div.right_contents.hover_box > div > ul > li > div.style-list-item__thumbnail > a')
        style_list = []

        for i in items:
            itemno = i['onclick'].split('\'')[1]
            style = Style()
            style.musinsa='https://store.musinsa.com/app/styles/views/'+itemno
            style.gender = gender
            style.type = style
            style_list.append(style)

        return style_list

def get_item_info(style):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
    }
    cookies = {
        '_gf': style.gender
    }

    response = requests.get(url=style.musinsa, headers=headers, cookies=cookies)
    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.select_one('#style_info > h2')
        style.title = title.text

        image_url = soup.select_one('#style_info > div.detail_slider_wrap > div > video')
        print(image_url['poster'])

def get_image(url):

    response = requests.get(url)
    if response.status_code == 200:
        data =response.content





def get_styles(style, gender):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
    }
    cookies = {
        '_gf': gender
    }

    url = 'https://store.musinsa.com/app/styles/lists?style_type='+style
    response = requests.get(url=url, headers=headers, cookies=cookies)

    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        total_page = soup.select(
            'body > div.wrap > div.right_area > form > div.right_contents.hover_box > div > div.thumbType-box.box > span.pagingNumber > span.totalPagingNum')
        total_page = total_page[0]
        total_page = (total_page.text.strip())

        return total_page if total_page != '' else 0

for gender in ['M', 'F']:

    style_list = ['american_casual', 'street_casual', 'easy_casual', 'dandy', 'formal_office', 'sport_casual',
'romantic',
'semi_formal',
'office',
'sports',
'retro',
'girlish',
'golf',
'chic',
'campus']

    itemno_list = []

    # for s in style_list:
    #     total_page = int(get_styles(s, gender))
    #     for p in range(total_page):
    #         page = str(p+1)
    #         itemno_list.extend(get_item_urls('https://store.musinsa.com/app/styles/lists?page='+page, gender, s))
    #
    # for item in itemno_list:
    #     get_item_info(item)



temp = Style()
temp.gender='M'
temp.musinsa='https://store.musinsa.com/app/styles/views/19123'
get_item_info(temp)