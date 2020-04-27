import requests
import json
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib as mpl
import matplotlib.ticker as ticker


url_sum = "https://api.covid19api.com/summary"

response_sum = requests.get(url_sum)
data_sum = response_sum.json()
# print(response_sum.status_code)


url_country_list = "https://pkgstore.datahub.io/core/country-list/data_json/data/8c458f2d15d9f2119654b29ede6e45b8/data_json.json"

response_country_data = requests.get(url_country_list)
country_data = response_country_data.json()

url_graph = f"https://api.covid19api.com/total/country/gr/status/confirmed"
# url_graph = "https://api.covid19api.com/country/china/status/confirmed/live"

response = requests.get(url_graph)

# print(response.status_code)

data_graph = response.json()

# print(data_graph[0]["Country"])

x = []
y = []

for i in range(0, len(data_graph)):
    # print("Date: {}, Cases: {}".format(data_graph[i]["Date"], data_graph[i]["Cases"]))
    # x.append(i)
    date = str(data_graph[i]["Date"])
    x.append(date[5:10])
    y.append(data_graph[i]["Cases"])

# https://www.geeksforgeeks.org/graph-plotting-in-python-set-1/
# https://towardsdatascience.com/customizing-plots-with-python-matplotlib-bcf02691931f
plt.style.use("dark_background")
# mpl.rcParams['lines.linewidth'] = 3
# mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=['#ff8400', 'g', 'b', 'y'])

fig, ax = plt.subplots(figsize=(10, 6))

y1 = [0, 2000]
x1 = [0, 50]

ax.plot(x, y,
        color="#ff8400",
        linewidth=1,
        marker="o",
        markerfacecolor="#ff8400",
        markersize="3.5"
        )

ax.plot(x1, y1,
        color="#ff00ff",
        linewidth=1,
        marker="o",
        markerfacecolor="#ff8400",
        markersize="3.5"
        )

# https://matplotlib.org/3.1.1/gallery/ticks_and_spines/tick-locators.html

# ax.xaxis.set_major_locator(ticker.AutoLocator())
ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())

ax.xaxis.set_major_locator(ticker.MaxNLocator(20))
# ax.xaxis.set_major_locator(ticker.LinearLocator(25))
# ax.xaxis.set_minor_locator(ticker.LinearLocator(25))
# ax.text(2, 50, "Text", fontsize=11)

fig.autofmt_xdate(rotation=45, ha="right")

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.grid(color="grey",
        linewidth=0.5,
        alpha=0.5
        )

ax.set_xlabel("Dates")
ax.set_ylabel("Cases")
ax.set_title(f"COVID-19 statistics for Greece")
ax.legend(["GR", "TEST"])

plt.savefig("graph.png", transparent=True)
plt.show()
