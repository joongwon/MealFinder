import requests
from bs4 import BeautifulSoup
import shutil
import os
from urllib import parse
from PIL import Image


def create_image_search_url(q):
    return 'https://www.google.co.kr/search?q=' + parse.quote(q) + '&tbm=isch'


def find_menu_image(menuname, width):
    url = create_image_search_url(menuname)
    # print(url)
    r = requests.get(url)
    html = r.text
    # with open('sample.html', 'wb+') as f:
        # f.write(html.encode('utf-8'))
    soup = BeautifulSoup(html, 'html.parser')
    try:
        selected_list = soup.select('#ires > table > tr > td > a > img')
    except IndexError:
        # print('html element not found')
        return
    for selected in selected_list:
        # print(selected)
        src = selected.get('src')
        # print(src)
        r = requests.get(src, stream=True, headers={'User-agent': 'Mozilla/5.0'})
        if r.status_code == 200:
            image = Image.open(r.raw)
            image = image.resize((width, int(image.height*width/image.width)))
            # image.show()
            # return ImageTk.PhotoImage(image)
            return image


if __name__ == '__main__':
    menu = input('급식메뉴이름:')
    # menu = '쌀밥'
    find_menu_image(menu, 100)
