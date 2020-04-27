# import io
import logging
# import os
from datetime import date
from datetime import datetime

import discord
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import requests
from discord.ext import commands
from discord.utils import find
from matplotlib.font_manager import FontProperties

from flag_functions import *
from list_filter import *

logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix=".")
bot.remove_command("help")


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="with data"))


url_sum = "https://api.covid19api.com/summary"
response_sum = requests.get(url_sum)
data_sum = response_sum.json()
# print(response_sum.status_code)

url_country_list = "https://pkgstore.datahub.io/core/country-list/data_json/data/8c458f2d15d9f2119654b29ede6e45b8/data_json.json"
response_country_data = requests.get(url_country_list)
country_data = response_country_data.json()


# print(response_country_data.status_code)


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


def get_keys(dictionary):
    keys = []

    for key in dictionary.keys():
        keys.append(key)

    return keys


def graph_maker(country_name, country_code):
    url_graph = f"https://api.covid19api.com/total/country/{country_code}/status/confirmed"
    response = requests.get(url_graph)
    data_graph = response.json()

    url_more_data = f"https://api.thevirustracker.com/free-api?countryTimeline={country_code}"
    response_more_data = requests.get(url_more_data)
    data_graph_more = response_more_data.json()

    x = []
    y = []
    y1 = []
    y2 = []
    y3 = []

    for i in range(0, len(data_graph)):
        # print("Date: {}, Cases: {}".format(data_graph[i]["Date"], data_graph[i]["Cases"]))
        # x.append(i)
        day = str(data_graph[i]["Date"][8:10])
        month = date_formatter(str(data_graph[i]["Date"][5:7]))
        dates = month + " " + day

        x.append(dates)
        y.append(data_graph[i]["Cases"])

    key_list = []

    length = len(data_graph_more["timelineitems"])

    for i in range(0, length):
        key_list.append(get_keys(data_graph_more["timelineitems"][i]))

    # print(key_list)

    k = key_list[0]

    for i in range(0, len(k) - 1):
        # print(k[i])
        y2.append(data_graph_more["timelineitems"][0][k[i]]["total_deaths"])
        # y3.append(data_graph_more["timelineitems"][0][k[i]]["total_recoveries"])

    # print(y2)

    if len(y2) < len(x):
        diff = len(x) - len(y2)
        for i in range(0, diff):
            y2.insert(0, 0)

    # if len(y3) < len(x):
    #     diff = len(x) - len(y3)
    #     for i in range(0, diff):
    #         y3.insert(0, 0)

    # print(list(data_graph_more["timelineitems"][i].keys()))
    # y2.append(data_graph_more["timelineitems"][i][date_keys[0]]["total_deaths"])
    # print(date_keys[0])

    # https://www.geeksforgeeks.org/graph-plotting-in-python-set-1/
    # https://towardsdatascience.com/customizing-plots-with-python-matplotlib-bcf02691931f
    plt.style.use("dark_background")

    fig, ax = plt.subplots(figsize=(6, 4), tight_layout=True)

    ax.plot(x, y,
            color="#F79F1F",
            linewidth=2)
    # marker="o",
    # markerfacecolor="#ff8400",
    # markersize="3.5"
    # )

    ax.plot(x, y2,
            color="#EA2027",
            linewidth=2
            )

    # ax.plot(x, y3,
    #         color="#4cd137",
    #         linewidth=2
    #         )

    # https://matplotlib.org/3.1.1/gallery/ticks_and_spines/tick-locators.html

    # ax.xaxis.set_major_locator(ticker.AutoLocator())
    # ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    # ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())

    # ax.xaxis.set_major_locator(ticker.MaxNLocator(20))
    ax.xaxis.set_major_locator(ticker.LinearLocator(10))
    # ax.xaxis.set_minor_locator(ticker.LinearLocator(25))

    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)

    fig.autofmt_xdate(rotation=45, ha="center")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    # ax.spines["left"].set_visible(False)

    ax.grid(color="grey",
            linewidth=0.5,
            alpha=0.5
            )

    ax.fill_between(x, 0, y, facecolor="#ff8400", alpha=0.25)
    ax.fill_between(x, 0, y2, facecolor="#EA2027", alpha=0.25)
    # ax.fill_between(x, 0, y3, facecolor="#4cd137", alpha=0.25)

    label_font = FontProperties()
    label_font.set_family("sans-serif")
    label_font.set_file("./Whitney-Font/whitney-medium.otf")
    label_font.set_size(18)
    label_pad = 15

    title_font = FontProperties()
    title_font.set_family("sans-serif")
    title_font.set_file("./Whitney-Font/whitney-semibold.otf")
    title_font.set_size(20)
    title_pad = 18

    # ax.set_xlabel("Timeline", labelpad=label_pad, fontproperties=label_font)
    # ax.set_ylabel("Cases", labelpad=label_pad, fontproperties=label_font)

    # ax.set_title(f"COVID-19 statistics for {country_name}", pad=title_pad, fontproperties=title_font)

    country_code_upper = str.upper(country_code)
    ax.legend(["Total", "Deaths"], prop={"size": 11})

    plt.savefig("graph.png", transparent=True)
    # plt.show()


@bot.event
async def on_guild_join(guild):
    general = find(lambda x: x.name == 'general', guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        embed = discord.Embed(
            title="Thanks for inviting me!",
            description="Use `.help` for more info.",
            timestamp=datetime.utcnow(),
            colour=discord.Color.blue()
        )
        embed.set_footer(text="Made by Tony4k#5870")
        await general.send(embed=embed)

    # @bot.event
    # async def on_guild_remove(guild):
    #     # general = find(lambda x: x.name == 'general', guild.text_channels)
    #     # channel = bot.get_channel(700388677133795430)
    #     embed = discord.Embed(
    #         title="Thanks for having me!",
    #         description=f"`Coronabot left the chat.`",
    #         timestamp=datetime.utcnow(),
    #         colour=discord.Color.blue()
    #     )
    #     embed.set_footer(text="Made by Tony4k#5870")
    #     await guild.send(embed=embed)


def stats_calc(cases, deaths, recovered):
    active = cases - deaths - recovered
    d_rate = (deaths * 100) / cases
    r_rate = (recovered * 100) / cases

    return active, d_rate, r_rate


@bot.command()
async def stats(ctx, *entries):
    name_list = [":file_folder: Cases:", ":skull: Deaths:", ":white_check_mark: Recovered:", ":hospital: Active:",
                 ":chart_with_upwards_trend: Mortality rate:",
                 ":chart_with_downwards_trend: Recovery rate:"]

    # print(entries)

    the_date = date.today()
    the_date_formatted = the_date.strftime("%B %d, %Y")

    countries = get_stats(data_sum, entries)

    # print(countries)

    if not entries:

        cases = countries[6][0][0]
        deaths = countries[6][1][0]
        recovered = countries[6][2][0]

        print(cases, deaths, recovered)

        the_stats = stats_calc(int(cases), int(deaths), int(recovered))

        embed = discord.Embed(
            title="Global COVID-19 statistics",
            description=the_date_formatted,
            timestamp=datetime.utcnow(),
            colour=discord.Color.blue()
        )
        embed.set_author(name="Coronabot", icon_url="https://i.imgur.com/wE5DmmZ.png")
        embed.set_thumbnail(url="https://i.imgur.com/RnTB2kt.png")

        embed.add_field(name=name_list[0], value=countries[0])
        embed.add_field(name=name_list[1], value=countries[1])
        embed.add_field(name=name_list[2], value=countries[2])
        embed.add_field(name=name_list[3], value=f"{format(the_stats[0], ',d')}", inline=True)
        embed.add_field(name=name_list[4], value=f"{round(the_stats[1], 1)}%", inline=True)
        embed.add_field(name=name_list[5], value=f"{round(the_stats[2], 1)}%", inline=True)

        embed.set_footer(text="Data from Johns Hopkins CSSE")

        await ctx.send(embed=embed)

    # elif str.lower(entries) == "korea-north" or str.lower(entries) == "north-korea":
    #     embed = discord.Embed(
    #         title=":no_entry:   WARNING   :no_entry:",
    #         timestamp=datetime.utcnow(),
    #         colour=discord.Color.red()
    #     )
    #     embed.set_author(name="Coronabot", icon_url="https://i.imgur.com/wE5DmmZ.png")
    #     embed.add_field(name="Message from the supreme leader:", value="It's none of your business.")
    #     embed.set_footer(text="Data by Joe Mama. Got' em.")
    #     await ctx.send(embed=embed)

    else:
        # if str.upper(entries) == "UK":
        #     entries = "GB"
        # elif str.lower(entries) == "korea" or str.lower(entries) == "south-korea":
        #     entries = "korea-south"
        # elif str.upper(entries) == "USA" or str.lower(entries) == "united-states" or str.lower(
        #         entries) == "united-states-of-america":
        #     entries = "US"

        if len(countries[0]) == 1:
            if countries[0][0] == 0:
                embed = discord.Embed(
                    title=f"COVID-19 statistics for {countries[3][0]} ({countries[4][0]})",
                    description=the_date_formatted,
                    timestamp=datetime.utcnow(),
                    colour=discord.Color.blue()
                )
                embed.set_author(name="Coronabot", icon_url="https://i.imgur.com/wE5DmmZ.png")

                embed.add_field(name=name_list[0], value="0", inline=True)
                embed.add_field(name=name_list[1], value="0", inline=True)
                embed.add_field(name=name_list[2], value="0", inline=True)

                embed.set_thumbnail(url=f"https://www.countryflags.io/{str.lower(countries[4][0])}/flat/64.png")
                embed.set_footer(text="Data from Johns Hopkins CSSE")

                await ctx.send(embed=embed)

            else:
                graph_maker(countries[3][0], countries[4][0])

                cases = countries[6][0]
                deaths = countries[6][1]
                recovered = countries[6][2]

                print(cases, deaths, recovered)

                the_stats = stats_calc(int(cases), int(deaths), int(recovered))

                embed = discord.Embed(
                    title=f"COVID-19 statistics for {countries[3][0]} ({countries[4][0]})",
                    description=the_date_formatted,
                    timestamp=datetime.utcnow(),
                    colour=discord.Color.blue()
                )
                embed.set_author(name="Coronabot", icon_url="https://i.imgur.com/wE5DmmZ.png")

                embed.add_field(name=name_list[0], value=countries[0][0], inline=True)
                embed.add_field(name=name_list[1], value=countries[1][0], inline=True)
                embed.add_field(name=name_list[2], value=countries[2][0], inline=True)
                embed.add_field(name=name_list[3], value=f"{format(the_stats[0], ',d')}", inline=True)
                embed.add_field(name=name_list[4], value=f"{round(the_stats[1], 1)}%", inline=True)
                embed.add_field(name=name_list[5], value=f"{round(the_stats[2], 1)}%", inline=True)

                with open("./graph.png", "rb") as f:
                    file = io.BytesIO(f.read())
                img = discord.File(file, filename="graph.png")

                embed.set_image(url="attachment://graph.png")

                embed.set_thumbnail(url=f"https://www.countryflags.io/{countries[4][0].lower()}/flat/64.png")
                embed.set_footer(text="Data from Johns Hopkins CSSE")

                await ctx.send(embed=embed, file=img)

                plt.clf()
                os.remove("./graph.png")

        else:
            await ctx.send("Support for multiple countries is coming soon!")

        # for i in range(len(data_sum["Countries"])):
        #     if data_sum["Countries"][i]["Slug"] == str.lower(entries) or data_sum["Countries"][i]["CountryCode"] == str.upper(entries):
        #
        #         # -- Name
        #         country = data_sum["Countries"][i]["Country"]
        #
        #         # -- Cases
        #         total_confirmed = data_sum["Countries"][i]["TotalConfirmed"]
        #         new_confirmed = data_sum["Countries"][i]["NewConfirmed"]
        #
        #         cases = total_confirmed + new_confirmed
        #
        #         country_code = str.lower(data_sum["Countries"][i]["CountryCode"])
        #
        #         if cases == 0:
        #
        #             embed = discord.Embed(
        #                 title=f"COVID-19 statistics for {country} ({str.upper(country_code)})",
        #                 description=the_date_formatted,
        #                 timestamp=datetime.utcnow(),
        #                 colour=discord.Color.blue()
        #             )
        #             embed.set_author(name="Coronabot", icon_url="https://i.imgur.com/wE5DmmZ.png")
        #             embed.add_field(name="Total cases:", value="0", inline=True)
        #             embed.add_field(name="Total deaths:", value="0", inline=True)
        #             embed.add_field(name="Total recovered:", value="0", inline=True)
        #
        #             embed.set_thumbnail(url=f"https://www.countryflags.io/{country_code}/flat/64.png")
        #             embed.set_footer(text="Data from Johns Hopkins CSSE")
        #
        #             await ctx.send(embed=embed)
        #
        #             break
        #
        #         else:
        #             if new_confirmed == 0:
        #                 cases = total_confirmed
        #
        #             else:
        #                 cases = str(total_confirmed) + " (+" + str(new_confirmed) + ")"
        #
        #             # -- Deaths
        #             total_deaths = data_sum["Countries"][i]["TotalDeaths"]
        #             new_deaths = data_sum["Countries"][i]["NewDeaths"]
        #             if new_deaths == 0:
        #                 deaths = total_deaths
        #             else:
        #                 deaths = str(total_deaths) + " (+" + str(new_deaths) + ")"
        #
        #             # -- Recovered
        #             total_recovered = data_sum["Countries"][i]["TotalRecovered"]
        #             new_recovered = data_sum["Countries"][i]["NewRecovered"]
        #             if new_recovered == 0:
        #                 recovered = total_recovered
        #             else:
        #                 recovered = str(total_recovered) + " (+" + str(new_recovered) + ")"
        #
        #             graph_maker(data_sum["Countries"][i]["Country"], str.lower(data_sum["Countries"][i]["CountryCode"]))
        #
        #             embed = discord.Embed(
        #                 title=f"COVID-19 statistics for {country} ({str.upper(country_code)})",
        #                 description=the_date_formatted,
        #                 timestamp=datetime.utcnow(),
        #                 colour=discord.Color.blue()
        #             )
        #             embed.set_author(name="Coronabot", icon_url="https://i.imgur.com/wE5DmmZ.png")
        #
        #             embed.add_field(name="___", value="Greece", inline=False)
        #             embed.add_field(name="Total cases:", value=f"{cases}", inline=True)
        #             embed.add_field(name="Total deaths:", value=f"{deaths}", inline=True)
        #             embed.add_field(name="Total recovered:", value=f"{recovered}", inline=True)
        #
        #             embed.add_field(name="___", value="United Kingdom", inline=False)
        #             embed.add_field(name="Total cases:", value=f"{cases}", inline=True)
        #             embed.add_field(name="Total deaths:", value=f"{deaths}", inline=True)
        #             embed.add_field(name="Total recovered:", value=f"{recovered}", inline=True)
        #
        #             with open("./graph.png", "rb") as f:
        #                 file = io.BytesIO(f.read())
        #             img = discord.File(file, filename="graph.png")
        #
        #             embed.set_image(url="attachment://graph.png")
        #
        #             country_code = str.lower(data_sum["Countries"][i]["CountryCode"])
        #
        #             # embed.set_thumbnail(url=f"https://www.countryflags.io/{country_code}/flat/64.png")
        #             embed.set_thumbnail(url="attachment://flag.png")
        #
        #             with open("./compiled_flags.png", "rb") as flag:
        #                 file_flag = io.BytesIO(flag.read())
        #             img_flag = discord.File(file_flag, filename="flag.png")
        #
        #             embed.set_footer(text="Data from Johns Hopkins CSSE")
        #
        #             await ctx.send(embed=embed, files=[img, img_flag])
        #
        #             plt.clf()
        #             os.remove("./graph.png")
        #             break
        # else:
        #     embed = discord.Embed(
        #         title="No record of that country.",
        #         description="To view the list of available countries use `.list`",
        #         timestamp=datetime.utcnow(),
        #         colour=discord.Color.blue()
        #     )
        #     embed.set_author(name="Coronabot", icon_url="https://i.imgur.com/wE5DmmZ.png")
        #     await ctx.send(embed=embed)


@bot.command()
async def list(ctx):
    country_list = ""

    for i in range(0, (len(country_data))):
        country_list += str(country_data[i]["Code"]) + ": " + str(country_data[i]["Name"]) + "\n"
        if len(country_list) >= 1900:
            await ctx.send("```" + country_list + "```")
            country_list = ""


@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Coronabot Cheat-sheet",
        color=discord.Color.orange()
    )
    embed.set_author(name="Coronabot", icon_url="https://i.imgur.com/wE5DmmZ.png")
    embed.add_field(name="`.help`", value="Shows this __cheat-sheet__.", inline=False)
    embed.add_field(name="`.list`", value="Shows the list of __country codes__.", inline=False)
    embed.add_field(name="`.stats <country-name` or `code>`",
                    value="Shows the current COVID-19 __stats__ of the specified country.", inline=False)
    embed.set_footer(text="NOTE: Country names with two or more parts must be connected with a dash (-).")
    await ctx.send(embed=embed)


bot.run("NzAwMzg4Njc3MTMzNzk1NDMw.XpjP_A.EZSuL-LNTyUbG8y_kxER6rVP_pM")
