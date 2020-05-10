import json
import requests


url_sum = "https://api.covid19api.com/summary"
response_sum = requests.get(url_sum)
data_sum = response_sum.json()

change_names = []

with open("country_populations.json") as json_file:
    data = json.load(json_file)

for i in range(0, len(data_sum["Countries"])):
    if data[i]["Country"] == data_sum["Countries"][i]["Country"]:
        print("OK")

    else:
        change_names.append(data[i]["Country"])
        print(change_names)
