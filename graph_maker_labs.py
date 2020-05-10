import requests
import json
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.font_manager import FontProperties
import numpy as np
from per_mil_pop_calc import *
from millify import millify


def date_formatter(number):
    month = ""
    if number == "01":
        month = "Jan"
    elif number == "02":
        month = "Feb"
    elif number == "03":
        month = "Mar"
    elif number == "04":
        month = "Apr"
    elif number == "05":
        month = "May"
    elif number == "06":
        month = "Jun"
    elif number == "07":
        month = "Jul"
    elif number == "08":
        month = "Aug"
    elif number == "09":
        month = "Sep"
    elif number == "10":
        month = "Oct"
    elif number == "11":
        month = "Nov"
    elif number == "12":
        month = "Dec"

    return month


def format_values(value, pos=None):
    prefixes = ["K", "M", "B", "G", "T", "P"]

    formatted_num = millify(value, precision=1, prefixes=prefixes)

    return formatted_num


def get_keys(dictionary):
    keys = []

    for key in dictionary.keys():
        keys.append(key)

    return keys


line_width = 1  # 1
font_size = 10
legend_size = 10
marker_size = 5  # 7
grid_opacity = 0.5
grid_line_widtch = 0.75

country_limit = 6


def graph_maker(graph_type, country_code, filename):
    url_cases = f"https://api.covid19api.com/total/country/{country_code}/status/confirmed"
    response_cases = requests.get(url_cases)
    data_cases = response_cases.json()

    # url_deaths = f"https://api.thevirustracker.com/free-api?countryTimeline={country_code}"
    url_deaths = f"https://api.covid19api.com/total/country/{country_code}/status/deaths"
    response_deaths = requests.get(url_deaths)
    data_deaths = response_deaths.json()

    # url_recovered = f"https://api.covid19api.com/total/country/{country_code}/status/recovered"
    # response_recovered = requests.get(url_recovered)
    # data_recovered = response_recovered.json()

    x = []
    y = []
    y1 = []
    # y2 = []

    for i in range(0, len(data_cases)):
        day = str(data_cases[i]["Date"][8:10])
        month = date_formatter(str(data_cases[i]["Date"][5:7]))
        dates = month + " " + day

        x.append(dates)
        y.append(data_cases[i]["Cases"])
        y1.append(data_deaths[i]["Cases"])
        # y2.append(data_recovered[i]["Cases"])

    # key_list = []
    #
    # length = len(data_deaths["timelineitems"])
    # for i in range(0, length):
    #     key_list.append(get_keys(data_deaths["timelineitems"][i]))
    #
    # k = key_list[0]
    #
    # for i in range(0, len(k) - 1):
    #     y1.append(data_deaths["timelineitems"][0][k[i]]["total_deaths"])
    #
    # x_len = len(x)
    # y1_len = len(y1)
    #
    # if y1_len < x_len:
    #     diff = x_len - y1_len
    #     for i in range(0, diff):
    #         y1.insert(0, 0)
    #
    # elif y1_len == x_len:
    #     pass
    #
    # else:
    #     diff = y1_len - x_len
    #     for i in range(0, diff):
    #         y1.pop(0)

    # https://www.geeksforgeeks.org/graph-plotting-in-python-set-1/
    # https://towardsdatascience.com/customizing-plots-with-python-matplotlib-bcf02691931f

    plt.style.use("dark_background")

    fig, ax = plt.subplots(dpi=150)

    # Plot confirmed cases

    ax.plot(x, y,
            color="#F79F1F",
            linewidth=line_width,
            marker=".",
            markerfacecolor="#F79F1F",
            markersize=marker_size
            )

    # Plot deaths

    ax.plot(x, y1,
            color="#EA2027",
            linewidth=line_width,
            marker=".",
            markerfacecolor="#EA2027",
            markersize=marker_size
            )

    # Plot recovered

    # ax.plot(x, y2,
    #         color="#4cd137",
    #         linewidth=line_width,
    #         marker=".",
    #         markerfacecolor="#4cd137",
    #         markersize=marker_size
    #         )

    # https://matplotlib.org/3.1.1/gallery/ticks_and_spines/tick-locators.html

    # ax.xaxis.set_major_locator(ticker.LinearLocator(10))
    ax.xaxis.set_major_locator(ticker.IndexLocator(base=20, offset=2))

    plt.xticks(fontsize=font_size)
    plt.yticks(fontsize=font_size)

    fig.autofmt_xdate(rotation=0, ha="center")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    ax.grid(which="both",
            axis="y",
            color="grey",
            linewidth=grid_line_widtch,
            alpha=grid_opacity
            )

    ax.fill_between(x, y1, y, facecolor="#ff8400", alpha=0.25)
    ax.fill_between(x, 0, y1, facecolor="#EA2027", alpha=0.25)

    title_font = FontProperties()
    title_font.set_family("sans-serif")
    title_font.set_file("./Whitney-Font/whitney-semibold.otf")
    title_font.set_size(14)
    title_pad = 18

    ax.legend(["Total", "Deaths"], prop={"size": legend_size}, fancybox=True, facecolor="0.25")

    if graph_type == "linear":
        ax.set_title(f"Linear graph", pad=title_pad, fontproperties=title_font)
        plt.yscale("linear")

    elif graph_type == "log":
        ax.set_title(f"Logarithmic graph", pad=title_pad, fontproperties=title_font)
        plt.yscale("log")
        plt.ylim(bottom=10)
        plt.minorticks_off()

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_values))

    plt.savefig(f"{filename}.png", transparent=True)
    # plt.show()
    fig.clear()
    plt.close(fig)


# graph_maker("linear", "gb", "mynameisjeff")


def graph_maker_bar(active, deaths, recovered, filename):
    x = ["Active cases", "Deaths", "Recovered"]
    y = [active, deaths, recovered]
    colours = ["#F79F1F", "#EA2027", "#4cd137"]

    plt.style.use("dark_background")

    fig, ax = plt.subplots(dpi=150)

    for i in range(0, len(x)):
        ax.bar(x[i], y[i], 0.75,
               align="center",
               color=colours[i]
               )

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_values))

    plt.minorticks_off()

    plt.xticks(fontsize=font_size)
    plt.yticks(fontsize=font_size)

    fig.autofmt_xdate(rotation=0, ha="center")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    ax.grid(which="both",
            axis="y",
            color="grey",
            linewidth=grid_line_widtch,
            alpha=grid_opacity
            )

    title_font = FontProperties()
    title_font.set_family("sans-serif")
    title_font.set_file("./Whitney-Font/whitney-semibold.otf")
    title_font.set_size(14)
    title_pad = 18

    ax.set_title(f"Bar chart", pad=title_pad, fontproperties=title_font)

    # ax.legend(["Total", "Deaths"], prop={"size": legend_size}, fancybox=True, facecolor="0.25")

    plt.savefig(f"{filename}.png", transparent=True)
    # plt.show()
    fig.clear()
    plt.close(fig)


# graph_maker_bar(100, 50, 20)


def graph_maker_list(country_code_list, filename, cases_type="confirmed", graph_type="linear"):
    country_code_list_upper = []

    x = []

    # colour_list = ["#ffa502", "#A3CB38", "#1289A7", "#D980FA", "#B53471", "#000000"]

    colour_list = ["#F44336", "#4CAF50", "#3F51B5", "#9C27B0", "#03A9F4", "#CDDC39"]

    if len(country_code_list) <= country_limit:

        plt.style.use("dark_background")

        fig, ax = plt.subplots(dpi=150)

        y = []

        # --- Loop this part

        for u in range(0, len(country_code_list)):

            url_graph = f"https://api.covid19api.com/total/country/{country_code_list[u]}/status/{cases_type}"
            response = requests.get(url_graph)
            data_graph = response.json()

            country_code_list_upper.append(str.upper(country_code_list[u]))

            if u == 0:
                for i in range(0, len(data_graph)):
                    day = str(data_graph[i]["Date"][8:10])
                    month = date_formatter(str(data_graph[i]["Date"][5:7]))
                    dates = month + " " + day

                    x.append(dates)

            y.append([])

            for i in range(0, len(data_graph)):
                value = per_mil_calculator(data_graph[i]["Country"], data_graph[i]["Cases"])
                y[u].append(value)

            ax.plot(x, y[u],
                    color=colour_list[u],
                    linewidth=line_width,
                    marker=".",
                    markerfacecolor=colour_list[u],
                    markersize=marker_size
                    )

            ax.fill_between(x, 0, y[u], facecolor=colour_list[u], alpha=0.25)

        # ---

        title_font = FontProperties()
        title_font.set_family("sans-serif")
        title_font.set_file("./Whitney-Font/whitney-semibold.otf")
        title_font.set_size(14)
        title_pad = 18

        if graph_type == "linear":
            ax.set_title(f"Linear graph", pad=title_pad, fontproperties=title_font)
            plt.yscale("linear")

        elif graph_type == "log":
            ax.set_title(f"Logarithmic graph", pad=title_pad, fontproperties=title_font)
            plt.yscale("log")
            plt.ylim(bottom=10)
            plt.minorticks_off()

        ax.xaxis.set_major_locator(ticker.LinearLocator(10))
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_values))

        plt.xticks(fontsize=font_size)
        plt.yticks(fontsize=font_size)

        fig.autofmt_xdate(rotation=45, ha="center")

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)

        ax.grid(which="both",
                axis="y",
                color="grey",
                linewidth=grid_line_widtch,
                alpha=grid_opacity
                )

        ax.legend(country_code_list_upper, prop={"size": legend_size}, fancybox=True, facecolor="0.25")

        plt.savefig(f"{filename}.png", transparent=True)
        # plt.show()
        fig.clear()
        plt.close(fig)


# graph_maker_list(["GR", "GB", "NL", "SE", "CH"])


def graph_maker_list_bar(numbers, country_codes, filename):
    x = country_codes
    y = numbers
    colour_list = ["#F44336", "#4CAF50", "#3F51B5", "#9C27B0", "#03A9F4", "#CDDC39"]

    plt.style.use("dark_background")

    fig, ax = plt.subplots(dpi=150)

    for i in range(0, len(x)):
        ax.bar(x[i], y[i], 0.75,
               align="center",
               color=colour_list[i]
               )

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_values))

    plt.minorticks_off()

    plt.xticks(fontsize=font_size)
    plt.yticks(fontsize=font_size)

    fig.autofmt_xdate(rotation=0, ha="center")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    ax.grid(which="both",
            axis="y",
            color="grey",
            linewidth=grid_line_widtch,
            alpha=grid_opacity
            )

    title_font = FontProperties()
    title_font.set_family("sans-serif")
    title_font.set_file("./Whitney-Font/whitney-semibold.otf")
    title_font.set_size(14)
    title_pad = 18

    ax.set_title(f"Bar chart", pad=title_pad, fontproperties=title_font)

    # ax.legend(["Total", "Deaths"], prop={"size": legend_size}, fancybox=True, facecolor="0.25")

    plt.savefig(f"{filename}.png", transparent=True)
    # plt.show()
    fig.clear()
    plt.close(fig)


# graph_maker_list_bar([250000, 20000, 15000, 100, 50], ["GR", "UK", "NL", "US", "PT"], ["Greece", "United Kingdom", "Netherlands", "United States of America", "Portugal"], 103948573850124857)
