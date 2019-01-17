import requests
from bs4 import BeautifulSoup
import html

site_dic = {"서울": "stu.sen.go.kr",
            "인천": "stu.ice.go.kr",
            "부산": "stu.pen.go.kr",
            "광주": "stu.gen.go.kr",
            "대전": "stu.dje.go.kr",
            "대구": "stu.dge.go.kr",
            "세종": "stu.sje.go.kr",
            "울산": "stu.use.go.kr",
            "경기": "stu.goe.go.kr",
            "강원": "stu.kwe.go.kr",
            "충북": "stu.cbe.go.kr",
            "충남": "stu.cne.go.kr",
            "경북": "stu.gbe.kr",
            "경남": "stu.gne.go.kr",
            "전북": "stu.jbe.go.kr",
            "전남": "stu.jne.go.kr",
            "제주": "stu.jje.go.kr"}
allergy_dic = {"1": "난류", "2": "우유", "3": "메밀", "4": "땅콩", "5": "대두", "6": "밀", "7": "고등어", "8": "게", "9": "새우",
               "10": "돼지고기", "11": "복숭아", "12": "토마토", "13": "아황산류", "14": "호두", "15": "닭고기", "16": "쇠고기", "17": "오징어",
               "18": "조개류(굴,전복,홍합 포함)"}


# method crawl. get school region, school code, year(YYYY), and month(MM).


def crawl(school_region, school_code, year, month, date):
    full_url = "http://" + site_dic[school_region] + "/sts_sci_md00_001.do?" + \
               "schulCode=" + school_code + "&schulCrseScCode=4&schulKndScCode=04&ay=" + year + \
               "&mm={0:02d}".format(int(month))

    r = requests.get(full_url)
    html_file = r.text
    soup = BeautifulSoup(html_file, "html.parser")
    soup.select('#contents > div:nth-child(2) > table > tbody')
    try:
        foods = html.unescape(str(soup.find_all("tr")).split("<div>" + date + "<br/>")[1].split("</div>")[0])
    except IndexError:
        return ""
    foods = foods.replace("<br/>", "\n")
    return foods


def get_allergy_text(nums):
    to_return = ""
    for next_allergy in nums.split('.')[:-1]:
        if not next_allergy == '':
            if int(next_allergy) > 18:
                next_allergy = next_allergy[1:]
        if next_allergy in allergy_dic:
            to_return += allergy_dic[next_allergy] + ", "
    return to_return[:-2]


