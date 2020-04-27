import os
import cairosvg
from bs4 import BeautifulSoup
import requests

# os.rename("./graph.txt", "./graph.svg")
#
# cairosvg.svg2png(url="graph.svg", write_to="graph.png")

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"}

url = "https://www.worldometers.info/coronavirus/country/greece/"

page = requests.get(url, headers=headers)
print(page.content)


soup = BeautifulSoup(page.content, "html.parser")
tag = soup.find_all("div", class_="highcharts-container")
# image = soup.find_all("<svg>", class_="highcharts-root")
# image = soup.find_all("svg", {"class": "highcharts-root"})

print(tag)

# whole_tag_contents = image[1].encode_contents()
# print(whole_tag_contents)
