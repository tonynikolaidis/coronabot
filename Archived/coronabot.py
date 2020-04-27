import discord
from discord.ext import commands
import requests
import json
import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import date
import datetime
from bs4 import BeautifulSoup


bot = commands.Bot(command_prefix=".")
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"}


@bot.command(pass_content=True)
async def image(ctx):
    img_file = open("./graph.png", "rb")
    img = discord.File(img_file)
    await ctx.send(file=img)
    img_file.close()


@bot.command()
async def status(ctx, country):

    if country == "world":
        url = "https://www.worldometers.info/coronavirus/#countries"

        page = requests.get(url, headers=headers)
        today = date.today()
        time = str(datetime.datetime.now().hour) + ":" + str(datetime.datetime.now().minute) + ":" + str(
            datetime.datetime.now().second)
        # print(time)
        soup = BeautifulSoup(page.content, "html.parser")

        numbers = soup.find_all(class_="maincounter-number")

        # print(numbers)

        the_list = []

        for numbers in numbers:
            the_list.append(numbers.text.strip())
            print(numbers.text.strip())

        # print(the_list)

        total_cases = the_list[0]
        total_deaths = the_list[1]
        total_recovered = the_list[2]
        await ctx.send(
            f"**World coronavirus cases**\n```Date: {today}\nTime: {time}\n\nTotal cases: {total_cases}\nTotal deaths: {total_deaths}\nTotal recovered: {total_recovered}```")

    if country == "north-korea":
        await ctx.send("None of your business boi.")

    else:
        url = f"https://www.worldometers.info/coronavirus/country/{country}/"

        page = requests.get(url, headers=headers)
        today = date.today()
        time = str(datetime.datetime.now().hour) + ":" + str(datetime.datetime.now().minute) + ":" + str(
            datetime.datetime.now().second)
        # print(time)
        soup = BeautifulSoup(page.content, "html.parser")

        numbers = soup.find_all(class_="maincounter-number")

        # print(numbers)

        the_list = []

        for numbers in numbers:
            the_list.append(numbers.text.strip())
            print(numbers.text.strip())

        # print(the_list)

        total_cases = the_list[0]
        total_deaths = the_list[1]
        total_recovered = the_list[2]
        await ctx.send(
            f"**{country} coronavirus cases**\n```Date: {today}\nTime: {time}\n\nTotal cases: {total_cases}\nTotal deaths: {total_deaths}\nTotal recovered: {total_recovered}```")
bot.run("NzAwMzg4Njc3MTMzNzk1NDMw.XpjP_A.EZSuL-LNTyUbG8y_kxER6rVP_pM")