import discord
from discord.ext import commands
from discord.utils import find
import requests
import matplotlib.pyplot as plt
import os
from datetime import date
from datetime import datetime
import io
import logging
import matplotlib.ticker as ticker


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


def graph_maker(country_name, country_code):
    url_graph = f"https://api.covid19api.com/total/country/{country_code}/status/confirmed"
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
        day = str(data_graph[i]["Date"][8:10])
        month = date_formatter(str(data_graph[i]["Date"][5:7]))
        dates = month + " " + day

        x.append(dates)
        y.append(data_graph[i]["Cases"])

    # https://www.geeksforgeeks.org/graph-plotting-in-python-set-1/
    # https://towardsdatascience.com/customizing-plots-with-python-matplotlib-bcf02691931f
    plt.style.use("dark_background")
    # mpl.rcParams['lines.linewidth'] = 3
    # mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=['#ff8400', 'g', 'b', 'y'])

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(x, y,
            color="#ff8400",
            linewidth=1,
            marker="o",
            markerfacecolor="#ff8400",
            markersize="3.5"
            )

    # https://matplotlib.org/3.1.1/gallery/ticks_and_spines/tick-locators.html

    # ax.xaxis.set_major_locator(ticker.AutoLocator())
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())

    # ax.xaxis.set_major_locator(ticker.MaxNLocator(20))
    ax.xaxis.set_major_locator(ticker.LinearLocator(20))
    # ax.xaxis.set_minor_locator(ticker.LinearLocator(25))
    # ax.text(2, 50, "Text", fontsize=11)

    fig.autofmt_xdate(rotation=45, ha="center")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.grid(color="grey",
            linewidth=0.5,
            alpha=0.5
            )

    ax.set_xlabel("Dates")
    ax.set_ylabel("Cases")
    ax.set_title(f"COVID-19 statistics for {country_name}")
    country_code_upper = str.upper(country_code)
    ax.legend([f"{country_code_upper}"])

    plt.savefig("graph.png", transparent=True)
    # plt.show()


@bot.event
async def on_guild_join(guild):
    general = find(lambda x: x.name == 'general', guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        embed = discord.Embed(
            title="Thanks for inviting me!",
            description="Use `.readme` for more info.",
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


@bot.command()
async def stats(ctx, entry):
    if str.lower(entry) == "world" or str.lower(entry) == "global" or str.lower(entry) == "all":
        # -- Cases
        total_confirmed = data_sum["Global"]["TotalConfirmed"]
        new_confirmed = data_sum["Global"]["NewConfirmed"]

        if new_confirmed == 0:
            cases = total_confirmed
        else:
            cases = str(total_confirmed) + " (+" + str(new_confirmed) + ")"

        # -- Deaths
        total_deaths = data_sum["Global"]["TotalDeaths"]
        new_deaths = data_sum["Global"]["NewDeaths"]
        if new_deaths == 0:
            deaths = total_deaths
        else:
            deaths = str(total_deaths) + " (+" + str(new_deaths) + ")"

        # -- Recovered
        total_recovered = data_sum["Global"]["TotalRecovered"]
        new_recovered = data_sum["Global"]["NewRecovered"]
        if new_recovered == 0:
            recovered = total_recovered
        else:
            recovered = str(total_recovered) + " (+" + str(new_recovered) + ")"

        the_date = date.today()
        the_date_formatted = the_date.strftime("%B %d, %Y")

        embed = discord.Embed(
            title="Global COVID-19 statistics",
            description=the_date_formatted,
            timestamp=datetime.utcnow(),
            colour=discord.Color.blue()
        )
        embed.set_author(name="Coronabot", icon_url="https://i.imgur.com/wE5DmmZ.png")
        embed.set_thumbnail(url="https://i.imgur.com/RnTB2kt.png")
        embed.add_field(name="Total cases:", value=f"{cases}")
        embed.add_field(name="Total deaths:", value=f"{deaths}")
        embed.add_field(name="Total recovered:", value=f"{recovered}")

        await ctx.send(embed=embed)

        # await ctx.send(
        #     f"**Global coronavirus cases**\n```Total cases:     {cases}\nTotal deaths:    {deaths}\nTotal recovered: {recovered}```")

    elif str.lower(entry) == "korea-north" or str.lower(entry) == "north-korea":
        embed = discord.Embed(
            title=":no_entry:   WARNING   :no_entry:",
            timestamp=datetime.utcnow(),
            colour=discord.Color.red()
        )
        embed.set_author(name="Coronabot", icon_url="https://i.imgur.com/wE5DmmZ.png")
        embed.add_field(name="Message from the supreme leader:", value="It's none of your business.")
        embed.set_footer(text="Data by Joe Mama. Got' em.")
        await ctx.send(embed=embed)

    else:
        if str.upper(entry) == "UK":
            entry = "GB"
        elif str.lower(entry) == "korea" or str.lower(entry) == "south-korea":
            entry = "korea-south"
        elif str.upper(entry) == "USA" or str.lower(entry) == "united-states" or str.lower(
                entry) == "united-states-of-america":
            entry = "US"

        for i in range(len(data_sum["Countries"])):
            if data_sum["Countries"][i]["Slug"] == str.lower(entry) or data_sum["Countries"][i]["CountryCode"] == str.upper(entry):
                # print(data_sum["Countries"][i]["Country"])

                # -- Name
                country = data_sum["Countries"][i]["Country"]

                # -- Cases
                total_confirmed = data_sum["Countries"][i]["TotalConfirmed"]
                new_confirmed = data_sum["Countries"][i]["NewConfirmed"]

                cases = total_confirmed + new_confirmed

                country_code = str.lower(data_sum["Countries"][i]["CountryCode"])

                if cases == 0:
                    the_date = date.today()
                    the_date_formatted = the_date.strftime("%B %d, %Y")

                    embed = discord.Embed(
                        title=f"COVID-19 statistics for {country} ({str.upper(country_code)})",
                        description=the_date_formatted,
                        timestamp=datetime.utcnow(),
                        colour=discord.Color.blue()
                    )
                    embed.set_author(name="Coronabot", icon_url="https://i.imgur.com/wE5DmmZ.png")
                    embed.add_field(name="Total cases:", value="0", inline=True)
                    embed.add_field(name="Total deaths:", value="0", inline=True)
                    embed.add_field(name="Total recovered:", value="0", inline=True)

                    embed.set_thumbnail(url=f"https://www.countryflags.io/{country_code}/flat/64.png")
                    embed.set_footer(text="Data from Johns Hopkins CSSE")

                    await ctx.send(embed=embed)

                    break

                else:
                    if new_confirmed == 0:
                        cases = total_confirmed

                    else:
                        cases = str(total_confirmed) + " (+" + str(new_confirmed) + ")"

                    # -- Deaths
                    total_deaths = data_sum["Countries"][i]["TotalDeaths"]
                    new_deaths = data_sum["Countries"][i]["NewDeaths"]
                    if new_deaths == 0:
                        deaths = total_deaths
                    else:
                        deaths = str(total_deaths) + " (+" + str(new_deaths) + ")"

                    # -- Recovered
                    total_recovered = data_sum["Countries"][i]["TotalRecovered"]
                    new_recovered = data_sum["Countries"][i]["NewRecovered"]
                    if new_recovered == 0:
                        recovered = total_recovered
                    else:
                        recovered = str(total_recovered) + " (+" + str(new_recovered) + ")"

                    # await ctx.send(
                    #     f"**{country} coronavirus cases**\n```Total cases:     {cases}\nTotal deaths:    {deaths}\nTotal recovered: {recovered}```")

                    graph_maker(data_sum["Countries"][i]["Country"], str.lower(data_sum["Countries"][i]["CountryCode"]))

                    the_date = date.today()
                    the_date_formatted = the_date.strftime("%B %d, %Y")

                    embed = discord.Embed(
                        title=f"COVID-19 statistics for {country} ({str.upper(country_code)})",
                        description=the_date_formatted,
                        timestamp=datetime.utcnow(),
                        colour=discord.Color.blue()
                    )
                    embed.set_author(name="Coronabot", icon_url="https://i.imgur.com/wE5DmmZ.png")
                    embed.add_field(name="Total cases:", value=f"{cases}", inline=True)
                    embed.add_field(name="Total deaths:", value=f"{deaths}", inline=True)
                    embed.add_field(name="Total recovered:", value=f"{recovered}", inline=True)

                    with open("./graph.png", "rb") as f:
                        file = io.BytesIO(f.read())
                    img = discord.File(file, filename="graph.png")

                    embed.set_image(url="attachment://graph.png")

                    country_code = str.lower(data_sum["Countries"][i]["CountryCode"])
                    # if country_code == "gb":
                    #     country_code = "uk"

                    embed.set_thumbnail(url=f"https://www.countryflags.io/{country_code}/flat/64.png")
                    embed.set_footer(text="Data from Johns Hopkins CSSE")

                    await ctx.send(file=img, embed=embed)

                    # img_file = open("./graph.png", "rb")

                    # await ctx.send(file=img)
                    # img.close()
                    plt.clf()
                    os.remove("./graph.png")
                    break
        else:
            embed = discord.Embed(
                title="No record of that country.",
                description="To view the list of available countries use `.list`",
                timestamp=datetime.utcnow(),
                colour=discord.Color.blue()
            )
            embed.set_author(name="Coronabot", icon_url="https://i.imgur.com/wE5DmmZ.png")
            await ctx.send(embed=embed)


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
        title="Coronabot Cheatsheet",
        color=discord.Color.orange()
    )
    embed.set_author(name="Coronabot", icon_url="https://i.imgur.com/wE5DmmZ.png")
    embed.add_field(name="`.help`", value="Shows this __cheatsheet__.", inline=False)
    embed.add_field(name="`.list`", value="Shows the list of __country codes__ as a DM.", inline=False)
    embed.add_field(name="`.stats <country-name` or `code>`", value="Shows the current COVID-19 __stats__ of the specified country.", inline=False)
    embed.set_footer(text="NOTE: Country names with two or more parts must be connected with a dash (-).")
    await ctx.send(embed=embed)


bot.run("NzAwMzg4Njc3MTMzNzk1NDMw.XpjP_A.EZSuL-LNTyUbG8y_kxER6rVP_pM")
