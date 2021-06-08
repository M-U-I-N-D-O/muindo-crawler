import requests
from bs4 import BeautifulSoup
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
}



def get_category_info(category):

    url = 'https://search.musinsa.com/category/'+category
    data = {}

    response = requests.get(url=url, headers=headers)

    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        category = soup.select_one('#location_category_1_depth')
        data['category-name'] = category.text
        sub_group = []
        brands = []
        list = soup.select('#category_list > dl > dd > ul > li > a')

        for item in list:
            sub = {}
            sub['display-name'] = item['data-value']
            sub['value'] = item['data-code']
            sub_group.append(sub)

        data['sub-group'] = sub_group
        list = soup.select('#best_brand_list > dl > dd > ul > li > a > span')

        for index in range(0, len(list), 3):
            brand = {
                'display-name' : list[index].text,
                'value' : list[index+1].text
            }
            brands.append(brand)

        data['brands'] = brands

        prices = set()

        list = soup.select('#price_range > ul > li > a > span')

        for p in list:

            price = p.text.split(' ~ ')
            price = [ value[:-1].replace(',','') for value in price if len(value) > 0]
            [ prices.add(int(value)) for value in price]

        prices = sorted(prices)
        data['prices'] = prices

    return data
ids = ['003', '022']
# for id in ids:
#     data.get('sub-category').append(get_category_info(id))

data = {'category' : 'pants', 'sub-category' : []}
data = []
data.append(get_category_info('007'))
data.append(get_category_info('009'))
filename = 'headwear.json'

# with open(filename, 'w', encoding='UTF-8') as file:
#     file.write(json.dumps(obj=data, indent=4, ensure_ascii=False))


