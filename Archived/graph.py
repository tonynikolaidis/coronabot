import requests
import json
import matplotlib.pyplot as plt
import matplotlib as mpl

url = "https://api.covid19api.com/total/country/us/status/confirmed"
# url = "https://api.covid19api.com/country/china/status/confirmed/live"

response = requests.get(url)

print(response.status_code)


def jprint(obj):
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


# jprint(response.json())

data = response.json()

print(data[0]["Country"])

x = []
cases_list = []

for i in range(0, len(data)):
    # print("Date: {}, Cases: {}".format(data[i]["Date"], data[i]["Cases"]))
    x.append(i)
    cases_list.append(data[i]["Cases"])


# https://www.geeksforgeeks.org/graph-plotting-in-python-set-1/
plt.style.use("dark_background")
mpl.rcParams['lines.linewidth'] = 3
mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=['#ff8400', 'g', 'b', 'y'])
plt.plot(x, cases_list)
plt.xlabel("Day")
plt.ylabel("Cases")
plt.title("Corona cases for Greece")
plt.savefig("graph.png", transparent=True)
plt.show()
