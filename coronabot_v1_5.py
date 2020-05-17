import asyncio
import logging

from datetime import date
from datetime import datetime

import discord
from discord.ext import commands
from discord.utils import find

from flag_functions import *
from graph_maker_labs import *
from list_filter import *

logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix=".")
bot.remove_command("help")

url_sum = "https://api.covid19api.com/summary"
response_sum = requests.get(url_sum)
data_sum = response_sum.json()

url_country_list = "https://pkgstore.datahub.io/core/country-list/data_json/data/8c458f2d15d9f2119654b29ede6e45b8/data_json.json"
response_country_data = requests.get(url_country_list)
country_data = response_country_data.json()

reactions = ["🗑️", "📈", "📉", "📊", "🧪", "💀"]

name_list = [
    ":test_tube: Confirmed",
    ":skull_crossbones: Deaths",
    ":white_check_mark: Recovered",
    ":hospital: Active cases",
    ":drop_of_blood: Mortality rate",
    ":dna: Recovery rate"
 ]

description_graph_type = [
    f"React with {reactions[2]} for a **log** chart or {reactions[3]} for a **bar** chart.",
    f"React with {reactions[1]} for a **linear** chart or {reactions[3]} for a **bar** chart.",
    f"React with {reactions[1]} for a **linear** chart or {reactions[2]} for a **log** chart."
]

description_cases_type = [
    f"React with {reactions[4]} to switch to **Cases**/1M population.",
    f"React with {reactions[5]} to switch to **Deaths**/1M population."
]

descriptions = [
    str(description_graph_type[0]),                                     # 0
    str(description_graph_type[1]),                                     # 1
    str(description_graph_type[2]),                                     # 2
    str(description_graph_type[0] + " " + description_cases_type[0]),   # 3
    str(description_graph_type[1] + " " + description_cases_type[0]),   # 4
    str(description_graph_type[2] + " " + description_cases_type[0]),   # 5
    str(description_graph_type[0] + " " + description_cases_type[1]),   # 6
    str(description_graph_type[1] + " " + description_cases_type[1]),   # 7
    str(description_graph_type[2] + " " + description_cases_type[1])    # 8
]

country_limit = 6

msg_info = []
graph_type = []
ctx_list = []
embed_list = []


def remove_messages():
    for i in range(0, len(msg_info)):
        if (datetime.today().timestamp() - msg_info[i]["Timestamp"]) > 604800:
            del msg_info[i]


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="with data"))


@bot.event
async def on_guild_join(guild):
    general = find(lambda x: x.name == 'general', guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        embed = discord.Embed(
            description="• Use `.stats <country-code/name>` to get started, e.g. `.stats us` to get statistics for the USA.\n\n• To see more options use `.help`.\n\n• Use `.info` to find out more about Coronabot.",
            timestamp=datetime.utcnow(),
            colour=discord.Color.blue()
        )
        embed.set_author(name="Thanks for inviting me!", icon_url="https://i.imgur.com/wE5DmmZ.png")
        embed.set_footer(text="Created by Tony4k#5870")
        await general.send(embed=embed)


async def on_reactions(payload):
    remove_messages()

    user_id = payload.user_id

    if user_id != bot.user.id:
        today = datetime.today()
        timestamp = today.timestamp()

        emoji_name = payload.emoji.name
        message_id = payload.message_id
        channel_id = payload.channel_id

        i = 0

        data_list = []

        for i in range(0, len(msg_info)):
            if msg_info[i]["MessageID"] == message_id:
                data_list.append(msg_info[i])
                break

        try:
            author_id = data_list[0]["MessageAuthor"]

            if emoji_name == reactions[0] and user_id == author_id:
                await bot.http.delete_message(channel_id, message_id)
                del msg_info[i]

            # -----------------------           LINEAR           -----------------------------

            elif emoji_name == reactions[1] and data_list[0]["GraphType"] != "linear" and data_list[0]["CountryCount"] == "single" and user_id == author_id:
                graph_maker("linear", data_list[0]["CountryCode"], data_list[0]["MessageID"])

                embed = discord.Embed(
                    description=descriptions[0],
                    timestamp=datetime.utcnow(),
                    colour=discord.Color.blue()
                )
                embed.set_author(name=f"COVID-19 statistics | {data_list[0]['CountryName']} ({data_list[0]['CountryCode']})", icon_url=f"https://www.countryflags.io/{data_list[0]['CountryCode']}/flat/64.png")

                embed.add_field(name=name_list[0], value=data_list[0]["CasesFormatted"], inline=True)
                embed.add_field(name=name_list[1], value=data_list[0]["DeathsFormatted"], inline=True)
                embed.add_field(name=name_list[2], value=data_list[0]["RecoveredFormatted"], inline=True)
                embed.add_field(name=name_list[3], value=f"**{format(data_list[0]['Active'], ',d')}**", inline=True)
                embed.add_field(name=name_list[4], value=f"**{round(data_list[0]['MortalityRate'], 1)}**%", inline=True)
                embed.add_field(name=name_list[5], value=f"**{round(data_list[0]['RecoveryRate'], 1)}**%", inline=True)

                with open(f"./{data_list[0]['MessageID']}.png", "rb") as f:
                    file = io.BytesIO(f.read())
                img = discord.File(file, filename=f"{data_list[0]['MessageID']}.png")

                embed.set_image(url=f"attachment://{data_list[0]['MessageID']}.png")

                # embed.set_thumbnail(url=f"https://www.countryflags.io/{data_list[0]['CountryCode']}/flat/64.png")

                embed.set_footer(text="Data from Johns Hopkins CSSE")

                get_ctx = data_list[0]["Context"]

                try:
                    await bot.http.delete_message(channel_id, message_id)
                except discord.NotFound:
                    pass
                msg = await get_ctx.send(embed=embed, file=img)

                msg_info[i]["GraphType"] = "linear"
                msg_info[i]["MessageObj"] = msg
                # embed_list.append(msg)

                # plt.clf()
                os.remove(f"./{data_list[0]['MessageID']}.png")

                msg_info[i]["MessageID"] = msg.id
                msg_info[i]["Timestamp"] = timestamp

                try:
                    # await msg.add_reaction(reactions[1])
                    await msg.add_reaction(reactions[2])
                    await msg.add_reaction(reactions[3])
                    await msg.add_reaction(reactions[0])
                except discord.NotFound:
                    pass

            # -----------------------           LOG           -----------------------------

            elif emoji_name == reactions[2] and data_list[0]["GraphType"] != "log" and data_list[0]["CountryCount"] == "single" and user_id == author_id:
                graph_maker("log", data_list[0]["CountryCode"], data_list[0]["MessageID"])

                embed = discord.Embed(
                    description=descriptions[1],
                    timestamp=datetime.utcnow(),
                    colour=discord.Color.blue()
                )
                embed.set_author(name=f"COVID-19 statistics | {data_list[0]['CountryName']} ({data_list[0]['CountryCode']})", icon_url=f"https://www.countryflags.io/{data_list[0]['CountryCode']}/flat/64.png")

                embed.add_field(name=name_list[0], value=data_list[0]["CasesFormatted"], inline=True)
                embed.add_field(name=name_list[1], value=data_list[0]["DeathsFormatted"], inline=True)
                embed.add_field(name=name_list[2], value=data_list[0]["RecoveredFormatted"], inline=True)
                embed.add_field(name=name_list[3], value=f"**{format(data_list[0]['Active'], ',d')}**", inline=True)
                embed.add_field(name=name_list[4], value=f"**{round(data_list[0]['MortalityRate'], 1)}**%", inline=True)
                embed.add_field(name=name_list[5], value=f"**{round(data_list[0]['RecoveryRate'], 1)}**%", inline=True)

                with open(f"./{data_list[0]['MessageID']}.png", "rb") as f:
                    file = io.BytesIO(f.read())
                img = discord.File(file, filename=f"{data_list[0]['MessageID']}.png")

                embed.set_image(url=f"attachment://{data_list[0]['MessageID']}.png")

                # embed.set_thumbnail(url=f"https://www.countryflags.io/{data_list[0]['CountryCode']}/flat/64.png")

                embed.set_footer(text="Data from Johns Hopkins CSSE")

                get_ctx = data_list[0]["Context"]

                try:
                    await bot.http.delete_message(channel_id, message_id)
                except discord.NotFound:
                    pass
                msg = await get_ctx.send(embed=embed, file=img)

                msg_info[i]["GraphType"] = "log"
                msg_info[i]["MessageObj"] = msg
                # embed_list.append(msg)

                # plt.clf()
                os.remove(f"./{data_list[0]['MessageID']}.png")

                msg_info[i]["MessageID"] = msg.id
                msg_info[i]["Timestamp"] = timestamp

                try:
                    await msg.add_reaction(reactions[1])
                    # await msg.add_reaction(reactions[2])
                    await msg.add_reaction(reactions[3])
                    await msg.add_reaction(reactions[0])
                except discord.NotFound:
                    pass

            # -----------------------           BAR-CHART           -----------------------------

            elif emoji_name == reactions[3] and data_list[0]["GraphType"] != "bar" and data_list[0]["CountryCount"] == "single" and user_id == author_id:
                graph_maker_bar(data_list[0]['Active'], data_list[0]["Deaths"], data_list[0]["Recovered"],
                                data_list[0]["MessageID"])

                embed = discord.Embed(
                    description=descriptions[2],
                    timestamp=datetime.utcnow(),
                    colour=discord.Color.blue()
                )
                embed.set_author(name=f"COVID-19 statistics | {data_list[0]['CountryName']} ({data_list[0]['CountryCode']})", icon_url=f"https://www.countryflags.io/{data_list[0]['CountryCode']}/flat/64.png")

                embed.add_field(name=name_list[0], value=data_list[0]["CasesFormatted"], inline=True)
                embed.add_field(name=name_list[1], value=data_list[0]["DeathsFormatted"], inline=True)
                embed.add_field(name=name_list[2], value=data_list[0]["RecoveredFormatted"], inline=True)
                embed.add_field(name=name_list[3], value=f"**{format(data_list[0]['Active'], ',d')}**", inline=True)
                embed.add_field(name=name_list[4], value=f"**{round(data_list[0]['MortalityRate'], 1)}**%", inline=True)
                embed.add_field(name=name_list[5], value=f"**{round(data_list[0]['RecoveryRate'], 1)}**%", inline=True)

                with open(f"./{data_list[0]['MessageID']}.png", "rb") as f:
                    file = io.BytesIO(f.read())
                img = discord.File(file, filename=f"{data_list[0]['MessageID']}.png")

                embed.set_image(url=f"attachment://{data_list[0]['MessageID']}.png")

                # embed.set_thumbnail(url=f"https://www.countryflags.io/{data_list[0]['CountryCode']}/flat/64.png")

                embed.set_footer(text="Data from Johns Hopkins CSSE")

                get_ctx = data_list[0]["Context"]

                try:
                    await bot.http.delete_message(channel_id, message_id)
                except discord.NotFound:
                    pass
                msg = await get_ctx.send(embed=embed, file=img)

                msg_info[i]["GraphType"] = "bar"
                msg_info[i]["MessageObj"] = msg
                # embed_list.append(msg)

                # plt.clf()
                os.remove(f"./{data_list[0]['MessageID']}.png")

                msg_info[i]["MessageID"] = msg.id
                msg_info[i]["Timestamp"] = timestamp

                try:
                    await msg.add_reaction(reactions[1])
                    await msg.add_reaction(reactions[2])
                    # await msg.add_reaction(reactions[3])
                    await msg.add_reaction(reactions[0])
                except discord.NotFound:
                    pass

            # -----------------------           LINEAR - MULTIPLE           -----------------------------

            elif emoji_name == reactions[1] and data_list[0]["GraphType"] != "linear" and data_list[0]["CountryCount"] == "multiple" and user_id == author_id:

                graph_maker_list(data_list[0]["CountryCode"], data_list[0]["MessageID"], data_list[0]["StatusType"], "linear")
                # compile_flags(data_list[0]["CountryCode"], data_list[0]["MessageID"])

                embed = None

                if data_list[0]["StatusType"] == "confirmed":
                    embed = discord.Embed(
                        description=descriptions[6],
                        timestamp=datetime.utcnow(),
                        colour=discord.Color.blue()
                    )
                    embed.set_author(name="Compare COVID-19 statistics (Cases/1M pop.)",
                                     icon_url="https://i.imgur.com/wE5DmmZ.png")

                    for I in range(0, len(data_list[0]["Cases"])):
                        embed.add_field(name=f":flag_{data_list[0]['CountryCode'][I].lower()}: {data_list[0]['CountryName'][I]} ({data_list[0]['CountryCode'][I]})", value="**{:,.1f}** C/1M".format(data_list[0]["Cases"][I]), inline=True)

                elif data_list[0]["StatusType"] == "deaths":
                    embed = discord.Embed(
                        description=descriptions[3],
                        timestamp=datetime.utcnow(),
                        colour=discord.Color.blue()
                    )
                    embed.set_author(name="Compare COVID-19 statistics (Deaths/1M pop.)",
                                     icon_url="https://i.imgur.com/wE5DmmZ.png")

                    for I in range(0, len(data_list[0]["Deaths"])):
                        embed.add_field(name=f":flag_{data_list[0]['CountryCode'][I].lower()}: {data_list[0]['CountryName'][I]} ({data_list[0]['CountryCode'][I]})",
                                        value="**{:,.1f}** D/1M".format(data_list[0]["Deaths"][I]), inline=True)

                with open(f"./{data_list[0]['MessageID']}.png", "rb") as f:
                    file = io.BytesIO(f.read())
                img = discord.File(file, filename=f"{data_list[0]['MessageID']}.png")

                embed.set_image(url=f"attachment://{data_list[0]['MessageID']}.png")

                # with open(f"./{data_list[0]['MessageID']}compiled_flags.png", "rb") as k:
                #     flags_file = io.BytesIO(k.read())
                # flags_img = discord.File(flags_file, filename=f"{data_list[0]['MessageID']}compiled_flags.png")

                # embed.set_thumbnail(url=f"attachment://{data_list[0]['MessageID']}compiled_flags.png")

                embed.set_footer(text="Data from Johns Hopkins CSSE")

                get_ctx = data_list[0]["Context"]

                try:
                    await bot.http.delete_message(channel_id, message_id)
                except discord.NotFound:
                    pass
                # msg = await get_ctx.send(embed=embed, files=[img, flags_img])
                msg = await get_ctx.send(embed=embed, file=img)

                msg_info[i]["GraphType"] = "linear"
                msg_info[i]["MessageObj"] = msg

                os.remove(f"./{data_list[0]['MessageID']}.png")
                # os.remove(f"./{data_list[0]['MessageID']}compiled_flags.png")

                msg_info[i]["MessageID"] = msg.id
                msg_info[i]["Timestamp"] = timestamp

                try:
                    if data_list[0]["StatusType"] == "confirmed":
                        # await msg.add_reaction(reactions[1])
                        await msg.add_reaction(reactions[2])
                        await msg.add_reaction(reactions[3])
                        # await msg.add_reaction(reactions[4])
                        await msg.add_reaction(reactions[5])
                        await msg.add_reaction(reactions[0])

                    elif data_list[0]["StatusType"] == "deaths":
                        # await msg.add_reaction(reactions[1])
                        await msg.add_reaction(reactions[2])
                        await msg.add_reaction(reactions[3])
                        await msg.add_reaction(reactions[4])
                        # await msg.add_reaction(reactions[5])
                        await msg.add_reaction(reactions[0])
                except discord.NotFound:
                    pass

            # -----------------------           LOG - MULTIPLE           -----------------------------

            elif emoji_name == reactions[2] and data_list[0]["GraphType"] != "log" and data_list[0]["CountryCount"] == "multiple" and user_id == author_id:

                graph_maker_list(data_list[0]["CountryCode"], data_list[0]["MessageID"], data_list[0]["StatusType"], "log")
                # compile_flags(data_list[0]["CountryCode"], data_list[0]["MessageID"])

                embed = None

                if data_list[0]["StatusType"] == "confirmed":
                    embed = discord.Embed(
                        description=descriptions[7],
                        timestamp=datetime.utcnow(),
                        colour=discord.Color.blue()
                    )
                    embed.set_author(name="Compare COVID-19 statistics (Cases/1M pop.)",
                                     icon_url="https://i.imgur.com/wE5DmmZ.png")

                    for I in range(0, len(data_list[0]["Cases"])):
                        embed.add_field(name=f":flag_{data_list[0]['CountryCode'][I].lower()}: {data_list[0]['CountryName'][I]} ({data_list[0]['CountryCode'][I]})",
                                        value="**{:,.1f}** C/1M".format(data_list[0]["Cases"][I]), inline=True)

                elif data_list[0]["StatusType"] == "deaths":
                    embed = discord.Embed(
                        description=descriptions[4],
                        timestamp=datetime.utcnow(),
                        colour=discord.Color.blue()
                    )
                    embed.set_author(name="Compare COVID-19 statistics (Deaths/1M pop.)",
                                     icon_url="https://i.imgur.com/wE5DmmZ.png")

                    for I in range(0, len(data_list[0]["Deaths"])):
                        embed.add_field(name=f":flag_{data_list[0]['CountryCode'][I].lower()}: {data_list[0]['CountryName'][I]} ({data_list[0]['CountryCode'][I]})",
                                        value="**{:,.1f}** D/1M".format(data_list[0]["Deaths"][I]), inline=True)

                with open(f"./{data_list[0]['MessageID']}.png", "rb") as f:
                    file = io.BytesIO(f.read())
                img = discord.File(file, filename=f"{data_list[0]['MessageID']}.png")

                embed.set_image(url=f"attachment://{data_list[0]['MessageID']}.png")

                # with open(f"./{data_list[0]['MessageID']}compiled_flags.png", "rb") as k:
                #     flags_file = io.BytesIO(k.read())
                # flags_img = discord.File(flags_file, filename=f"{data_list[0]['MessageID']}compiled_flags.png")

                # embed.set_thumbnail(url=f"attachment://{data_list[0]['MessageID']}compiled_flags.png")

                embed.set_footer(text="Data from Johns Hopkins CSSE")

                get_ctx = data_list[0]["Context"]

                try:
                    await bot.http.delete_message(channel_id, message_id)
                except discord.NotFound:
                    pass
                # msg = await get_ctx.send(embed=embed, files=[img, flags_img])
                msg = await get_ctx.send(embed=embed, file=img)

                msg_info[i]["GraphType"] = "log"
                msg_info[i]["MessageObj"] = msg

                os.remove(f"./{data_list[0]['MessageID']}.png")
                # os.remove(f"./{data_list[0]['MessageID']}compiled_flags.png")

                msg_info[i]["MessageID"] = msg.id
                msg_info[i]["Timestamp"] = timestamp

                try:
                    if data_list[0]["StatusType"] == "confirmed":
                        await msg.add_reaction(reactions[1])
                        # await msg.add_reaction(reactions[2])
                        await msg.add_reaction(reactions[3])
                        # await msg.add_reaction(reactions[4])
                        await msg.add_reaction(reactions[5])
                        await msg.add_reaction(reactions[0])

                    elif data_list[0]["StatusType"] == "deaths":
                        await msg.add_reaction(reactions[1])
                        # await msg.add_reaction(reactions[2])
                        await msg.add_reaction(reactions[3])
                        await msg.add_reaction(reactions[4])
                        # await msg.add_reaction(reactions[5])
                        await msg.add_reaction(reactions[0])
                except discord.NotFound:
                    pass

            # -----------------------           BAR  - MULTIPLE           -----------------------------

            elif emoji_name == reactions[3] and data_list[0]["GraphType"] != "bar" and data_list[0]["CountryCount"] == "multiple" and user_id == author_id:

                # compile_flags(data_list[0]["CountryCode"], data_list[0]["MessageID"])

                embed = None

                if data_list[0]["StatusType"] == "confirmed":
                    graph_maker_list_bar(data_list[0]["Cases"], data_list[0]["CountryCode"], data_list[0]["MessageID"])

                    embed = discord.Embed(
                        description=descriptions[8],
                        timestamp=datetime.utcnow(),
                        colour=discord.Color.blue()
                    )
                    embed.set_author(name="Compare COVID-19 statistics (Cases/1M pop.)", icon_url="https://i.imgur.com/wE5DmmZ.png")

                    for I in range(0, len(data_list[0]["Cases"])):
                        embed.add_field(name=f":flag_{data_list[0]['CountryCode'][I].lower()}: {data_list[0]['CountryName'][I]} ({data_list[0]['CountryCode'][I]})",
                                        value="**{:,.1f}** C/1M".format(data_list[0]["Cases"][I]), inline=True)

                elif data_list[0]["StatusType"] == "deaths":
                    graph_maker_list_bar(data_list[0]["Deaths"], data_list[0]["CountryCode"], data_list[0]["MessageID"])

                    embed = discord.Embed(
                        description=descriptions[5],
                        timestamp=datetime.utcnow(),
                        colour=discord.Color.blue()
                    )
                    embed.set_author(name="Compare COVID-19 statistics (Deaths/1M pop.)", icon_url="https://i.imgur.com/wE5DmmZ.png")

                    for I in range(0, len(data_list[0]["Deaths"])):
                        embed.add_field(name=f":flag_{data_list[0]['CountryCode'][I].lower()}: {data_list[0]['CountryName'][I]} ({data_list[0]['CountryCode'][I]})",
                                        value="**{:,.1f}** D/1M".format(data_list[0]["Deaths"][I]), inline=True)

                with open(f"./{data_list[0]['MessageID']}.png", "rb") as f:
                    file = io.BytesIO(f.read())
                img = discord.File(file, filename=f"{data_list[0]['MessageID']}.png")

                embed.set_image(url=f"attachment://{data_list[0]['MessageID']}.png")

                # with open(f"./{data_list[0]['MessageID']}compiled_flags.png", "rb") as k:
                #     flags_file = io.BytesIO(k.read())
                # flags_img = discord.File(flags_file, filename=f"{data_list[0]['MessageID']}compiled_flags.png")

                # embed.set_thumbnail(url=f"attachment://{data_list[0]['MessageID']}compiled_flags.png")

                embed.set_footer(text="Data from Johns Hopkins CSSE")

                get_ctx = data_list[0]["Context"]

                try:
                    await bot.http.delete_message(channel_id, message_id)
                except discord.NotFound:
                    pass
                # msg = await get_ctx.send(embed=embed, files=[img, flags_img])
                msg = await get_ctx.send(embed=embed, file=img)

                msg_info[i]["GraphType"] = "bar"
                msg_info[i]["MessageObj"] = msg

                os.remove(f"./{data_list[0]['MessageID']}.png")
                # os.remove(f"./{data_list[0]['MessageID']}compiled_flags.png")

                msg_info[i]["MessageID"] = msg.id
                msg_info[i]["Timestamp"] = timestamp

                try:
                    if data_list[0]["StatusType"] == "confirmed":
                        await msg.add_reaction(reactions[1])
                        await msg.add_reaction(reactions[2])
                        # await msg.add_reaction(reactions[3])
                        # await msg.add_reaction(reactions[4])
                        await msg.add_reaction(reactions[5])
                        await msg.add_reaction(reactions[0])

                    elif data_list[0]["StatusType"] == "deaths":
                        await msg.add_reaction(reactions[1])
                        await msg.add_reaction(reactions[2])
                        # await msg.add_reaction(reactions[3])
                        await msg.add_reaction(reactions[4])
                        # await msg.add_reaction(reactions[5])
                        await msg.add_reaction(reactions[0])
                except discord.NotFound:
                    pass

            # -----------------------           CHANGE TO CASES/DEATHS           -----------------------------

            elif (emoji_name == reactions[4] or emoji_name == reactions[5]) and data_list[0]["CountryCount"] == "multiple" and user_id == author_id:
                if data_list[0]["StatusType"] != "deaths":
                    msg_info[i]["StatusType"] = "deaths"
                    data_list[0]["StatusType"] = "deaths"

                elif data_list[0]["StatusType"] != "confirmed":
                    msg_info[i]["StatusType"] = "confirmed"
                    data_list[0]["StatusType"] = "confirmed"

                # -- Resend linear --

                if data_list[0]["GraphType"] == "linear":
                    graph_maker_list(data_list[0]["CountryCode"], data_list[0]["MessageID"], data_list[0]["StatusType"], "linear")
                    # compile_flags(data_list[0]["CountryCode"], data_list[0]["MessageID"])

                    embed = None

                    if data_list[0]["StatusType"] == "confirmed":
                        embed = discord.Embed(
                            description=descriptions[6],
                            timestamp=datetime.utcnow(),
                            colour=discord.Color.blue()
                        )
                        embed.set_author(name="Compare COVID-19 statistics (Cases/1M pop.)",
                                         icon_url="https://i.imgur.com/wE5DmmZ.png")

                        for I in range(0, len(data_list[0]["Cases"])):
                            embed.add_field(
                                name=f":flag_{data_list[0]['CountryCode'][I].lower()}: {data_list[0]['CountryName'][I]} ({data_list[0]['CountryCode'][I]})",
                                value="**{:,.1f}** C/1M".format(data_list[0]["Cases"][I]), inline=True)

                    elif data_list[0]["StatusType"] == "deaths":
                        embed = discord.Embed(
                            description=descriptions[3],
                            timestamp=datetime.utcnow(),
                            colour=discord.Color.blue()
                        )
                        embed.set_author(name="Compare COVID-19 statistics (Deaths/1M pop.)",
                                         icon_url="https://i.imgur.com/wE5DmmZ.png")

                        for I in range(0, len(data_list[0]["Deaths"])):
                            embed.add_field(
                                name=f":flag_{data_list[0]['CountryCode'][I].lower()}: {data_list[0]['CountryName'][I]} ({data_list[0]['CountryCode'][I]})",
                                value="**{:,.1f}** D/1M".format(data_list[0]["Deaths"][I]), inline=True)

                    with open(f"./{data_list[0]['MessageID']}.png", "rb") as f:
                        file = io.BytesIO(f.read())
                    img = discord.File(file, filename=f"{data_list[0]['MessageID']}.png")

                    embed.set_image(url=f"attachment://{data_list[0]['MessageID']}.png")

                    # with open(f"./{data_list[0]['MessageID']}compiled_flags.png", "rb") as k:
                    #     flags_file = io.BytesIO(k.read())
                    # flags_img = discord.File(flags_file, filename=f"{data_list[0]['MessageID']}compiled_flags.png")

                    # embed.set_thumbnail(url=f"attachment://{data_list[0]['MessageID']}compiled_flags.png")

                    embed.set_footer(text="Data from Johns Hopkins CSSE")

                    get_ctx = data_list[0]["Context"]

                    try:
                        await bot.http.delete_message(channel_id, message_id)
                    except discord.NotFound:
                        pass
                    # msg = await get_ctx.send(embed=embed, files=[img, flags_img])
                    msg = await get_ctx.send(embed=embed, file=img)

                    msg_info[i]["GraphType"] = "linear"
                    msg_info[i]["MessageObj"] = msg

                    os.remove(f"./{data_list[0]['MessageID']}.png")
                    # os.remove(f"./{data_list[0]['MessageID']}compiled_flags.png")

                    msg_info[i]["MessageID"] = msg.id
                    msg_info[i]["Timestamp"] = timestamp

                    try:
                        if data_list[0]["StatusType"] == "confirmed":
                            # await msg.add_reaction(reactions[1])
                            await msg.add_reaction(reactions[2])
                            await msg.add_reaction(reactions[3])
                            # await msg.add_reaction(reactions[4])
                            await msg.add_reaction(reactions[5])
                            await msg.add_reaction(reactions[0])

                        elif data_list[0]["StatusType"] == "deaths":
                            # await msg.add_reaction(reactions[1])
                            await msg.add_reaction(reactions[2])
                            await msg.add_reaction(reactions[3])
                            await msg.add_reaction(reactions[4])
                            # await msg.add_reaction(reactions[5])
                            await msg.add_reaction(reactions[0])
                    except discord.NotFound:
                        pass

                # -- Resend log --

                elif data_list[0]["GraphType"] == "log":
                    graph_maker_list(data_list[0]["CountryCode"], data_list[0]["MessageID"], data_list[0]["StatusType"], "log")
                    # compile_flags(data_list[0]["CountryCode"], data_list[0]["MessageID"])

                    embed = None

                    if data_list[0]["StatusType"] == "confirmed":
                        embed = discord.Embed(
                            description=descriptions[7],
                            timestamp=datetime.utcnow(),
                            colour=discord.Color.blue()
                        )
                        embed.set_author(name="Compare COVID-19 statistics (Cases/1M pop.)",
                                         icon_url="https://i.imgur.com/wE5DmmZ.png")

                        for I in range(0, len(data_list[0]["Cases"])):
                            embed.add_field(
                                name=f":flag_{data_list[0]['CountryCode'][I].lower()}: {data_list[0]['CountryName'][I]} ({data_list[0]['CountryCode'][I]})",
                                value="**{:,.1f}** C/1M".format(data_list[0]["Cases"][I]), inline=True)

                    elif data_list[0]["StatusType"] == "deaths":
                        embed = discord.Embed(
                            description=descriptions[4],
                            timestamp=datetime.utcnow(),
                            colour=discord.Color.blue()
                        )
                        embed.set_author(name="Compare COVID-19 statistics (Deaths/1M pop.)",
                                         icon_url="https://i.imgur.com/wE5DmmZ.png")

                        for I in range(0, len(data_list[0]["Deaths"])):
                            embed.add_field(
                                name=f":flag_{data_list[0]['CountryCode'][I].lower()}: {data_list[0]['CountryName'][I]} ({data_list[0]['CountryCode'][I]})",
                                value="**{:,.1f}** D/1M".format(data_list[0]["Deaths"][I]), inline=True)

                    embed.set_author(name="Coronabot", icon_url="https://i.imgur.com/wE5DmmZ.png")

                    with open(f"./{data_list[0]['MessageID']}.png", "rb") as f:
                        file = io.BytesIO(f.read())
                    img = discord.File(file, filename=f"{data_list[0]['MessageID']}.png")

                    embed.set_image(url=f"attachment://{data_list[0]['MessageID']}.png")

                    # with open(f"./{data_list[0]['MessageID']}compiled_flags.png", "rb") as k:
                    #     flags_file = io.BytesIO(k.read())
                    # flags_img = discord.File(flags_file, filename=f"{data_list[0]['MessageID']}compiled_flags.png")
                    #
                    # embed.set_thumbnail(url=f"attachment://{data_list[0]['MessageID']}compiled_flags.png")

                    embed.set_footer(text="Data from Johns Hopkins CSSE")

                    get_ctx = data_list[0]["Context"]

                    try:
                        await bot.http.delete_message(channel_id, message_id)
                    except discord.NotFound:
                        pass
                    # msg = await get_ctx.send(embed=embed, files=[img, flags_img])
                    msg = await get_ctx.send(embed=embed, file=img)

                    msg_info[i]["GraphType"] = "log"
                    msg_info[i]["MessageObj"] = msg

                    os.remove(f"./{data_list[0]['MessageID']}.png")
                    # os.remove(f"./{data_list[0]['MessageID']}compiled_flags.png")

                    msg_info[i]["MessageID"] = msg.id
                    msg_info[i]["Timestamp"] = timestamp

                    try:
                        if data_list[0]["StatusType"] == "confirmed":
                            await msg.add_reaction(reactions[1])
                            # await msg.add_reaction(reactions[2])
                            await msg.add_reaction(reactions[3])
                            # await msg.add_reaction(reactions[4])
                            await msg.add_reaction(reactions[5])
                            await msg.add_reaction(reactions[0])

                        elif data_list[0]["StatusType"] == "deaths":
                            await msg.add_reaction(reactions[1])
                            # await msg.add_reaction(reactions[2])
                            await msg.add_reaction(reactions[3])
                            await msg.add_reaction(reactions[4])
                            # await msg.add_reaction(reactions[5])
                            await msg.add_reaction(reactions[0])
                    except discord.NotFound:
                        pass

                # -- Resend bar --

                elif data_list[0]["GraphType"] == "bar":
                    # compile_flags(data_list[0]["CountryCode"], data_list[0]["MessageID"])

                    embed = None

                    if data_list[0]["StatusType"] == "confirmed":
                        graph_maker_list_bar(data_list[0]["Cases"], data_list[0]["CountryCode"],
                                             data_list[0]["MessageID"])

                        embed = discord.Embed(
                            description=descriptions[8],
                            timestamp=datetime.utcnow(),
                            colour=discord.Color.blue()
                        )
                        embed.set_author(name="Compare COVID-19 statistics (Cases/1M pop.)",
                                         icon_url="https://i.imgur.com/wE5DmmZ.png")

                        for I in range(0, len(data_list[0]["Cases"])):
                            embed.add_field(
                                name=f":flag_{data_list[0]['CountryCode'][I].lower()}: {data_list[0]['CountryName'][I]} ({data_list[0]['CountryCode'][I]})",
                                value="**{:,.1f}** C/1M".format(data_list[0]["Cases"][I]), inline=True)

                    elif data_list[0]["StatusType"] == "deaths":
                        graph_maker_list_bar(data_list[0]["Deaths"], data_list[0]["CountryCode"],
                                             data_list[0]["MessageID"])

                        embed = discord.Embed(
                            description=descriptions[5],
                            timestamp=datetime.utcnow(),
                            colour=discord.Color.blue()
                        )
                        embed.set_author(name="Compare COVID-19 statistics (Deaths/1M pop.)", icon_url="https://i.imgur.com/wE5DmmZ.png")

                        for I in range(0, len(data_list[0]["Deaths"])):
                            embed.add_field(
                                name=f":flag_{data_list[0]['CountryCode'][I].lower()}: {data_list[0]['CountryName'][I]} ({data_list[0]['CountryCode'][I]})",
                                value="**{:,.1f}** D/1M".format(data_list[0]["Deaths"][I]), inline=True)

                    with open(f"./{data_list[0]['MessageID']}.png", "rb") as f:
                        file = io.BytesIO(f.read())
                    img = discord.File(file, filename=f"{data_list[0]['MessageID']}.png")

                    embed.set_image(url=f"attachment://{data_list[0]['MessageID']}.png")

                    # with open(f"./{data_list[0]['MessageID']}compiled_flags.png", "rb") as k:
                    #     flags_file = io.BytesIO(k.read())
                    # flags_img = discord.File(flags_file, filename=f"{data_list[0]['MessageID']}compiled_flags.png")
                    #
                    # embed.set_thumbnail(url=f"attachment://{data_list[0]['MessageID']}compiled_flags.png")

                    embed.set_footer(text="Data from Johns Hopkins CSSE")

                    get_ctx = data_list[0]["Context"]
                    try:
                        await bot.http.delete_message(channel_id, message_id)
                    except discord.NotFound:
                        pass
                    msg = await get_ctx.send(embed=embed, file=img)

                    msg_info[i]["GraphType"] = "bar"
                    msg_info[i]["MessageObj"] = msg

                    os.remove(f"./{data_list[0]['MessageID']}.png")
                    # os.remove(f"./{data_list[0]['MessageID']}compiled_flags.png")

                    msg_info[i]["MessageID"] = msg.id
                    msg_info[i]["Timestamp"] = timestamp

                    try:
                        if data_list[0]["StatusType"] == "confirmed":
                            await msg.add_reaction(reactions[1])
                            await msg.add_reaction(reactions[2])
                            # await msg.add_reaction(reactions[3])
                            # await msg.add_reaction(reactions[4])
                            await msg.add_reaction(reactions[5])
                            await msg.add_reaction(reactions[0])

                        elif data_list[0]["StatusType"] == "deaths":
                            await msg.add_reaction(reactions[1])
                            await msg.add_reaction(reactions[2])
                            # await msg.add_reaction(reactions[3])
                            await msg.add_reaction(reactions[4])
                            # await msg.add_reaction(reactions[5])
                            await msg.add_reaction(reactions[0])
                    except discord.NotFound:
                        pass

        except IndexError:
            pass


reaction_queue = []


@bot.event
async def on_raw_reaction_add(payload):
    reaction_queue.append(payload)
    tasks = []

    for i in range(0, len(reaction_queue)):
        task = asyncio.create_task(on_reactions(reaction_queue[i]))
        tasks.append(task)

    reaction_queue.clear()
    await asyncio.gather(*tasks)


def stats_calc(cases, deaths, recovered):
    active = cases - deaths - recovered
    d_rate = (deaths * 100) / cases
    r_rate = (recovered * 100) / cases

    return active, d_rate, r_rate


async def make_stats_embed(ctx, entries, graph_file_name):
    remove_messages()

    the_date = date.today()
    the_date_formatted = the_date.strftime("%B %d, %Y")
    today = datetime.today()
    timestamp = today.timestamp()

    countries = get_stats(data_sum, entries)

    if not entries:

        cases = countries[6][0][0]
        deaths = countries[6][1][0]
        recovered = countries[6][2][0]

        # print(cases, deaths, recovered)

        the_stats = stats_calc(int(cases), int(deaths), int(recovered))

        embed = discord.Embed(
            # title="Global COVID-19 statistics",
            # description=the_date_formatted,
            timestamp=datetime.utcnow(),
            colour=discord.Color.blue()
        )
        embed.set_author(name="Global COVID-19 statistics", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Flag_of_the_United_Nations.svg/320px-Flag_of_the_United_Nations.svg.png")
        # embed.set_thumbnail(url="https://i.imgur.com/RnTB2kt.png")

        embed.add_field(name=name_list[0], value=f"{countries[0]}")
        embed.add_field(name=name_list[1], value=f"{countries[1]}")
        embed.add_field(name=name_list[2], value=f"{countries[2]}")
        embed.add_field(name=name_list[3], value=f"**{format(the_stats[0], ',d')}**", inline=True)
        embed.add_field(name=name_list[4], value=f"**{round(the_stats[1], 1)}**%", inline=True)
        embed.add_field(name=name_list[5], value=f"**{round(the_stats[2], 1)}**%", inline=True)

        embed.set_footer(text="Data from Johns Hopkins CSSE")

        msg = await ctx.send(embed=embed)

        msg_info.append(
            {
                "MessageID": msg.id,
                "MessageObj": msg,
                "MessageAuthor": ctx.author.id,
                "Context": ctx,
                "Timestamp": timestamp
            }
        )

        await msg.add_reaction(reactions[0])

    else:

        if len(countries[0]) == 1:
            if countries[0][0] == 0:
                embed = discord.Embed(
                    title=f"COVID-19 statistics | {countries[3][0]} ({countries[4][0]})",
                    timestamp=datetime.utcnow(),
                    colour=discord.Color.blue()
                )
                embed.set_author(name=f"COVID-19 statistics | {countries[3][0]} ({countries[4][0]})", icon_url=f"https://www.countryflags.io/{countries[4][0]}/flat/64.png")

                embed.add_field(name=name_list[0], value="**0**", inline=True)
                embed.add_field(name=name_list[1], value="**0**", inline=True)
                embed.add_field(name=name_list[2], value="**0**", inline=True)

                # embed.set_thumbnail(url=f"https://www.countryflags.io/{str.lower(countries[4][0])}/flat/64.png")
                embed.set_footer(text="Data from Johns Hopkins CSSE")

                msg = await ctx.send(embed=embed)

                msg_info.append(
                    {
                        "MessageID": msg.id,
                        "MessageObj": msg,
                        "MessageAuthor": ctx.author.id,
                        "Context": ctx,
                        "Timestamp": timestamp
                    }
                )

                await msg.add_reaction(reactions[0])

            else:
                graph_maker("linear", countries[4][0], graph_file_name)

                cases = countries[6][0]
                deaths = countries[6][1]
                recovered = countries[6][2]

                the_stats = stats_calc(int(cases), int(deaths), int(recovered))

                embed = discord.Embed(
                    description=descriptions[0],
                    timestamp=datetime.utcnow(),
                    colour=discord.Color.blue()
                )
                # embed.set_author(name=f"Coronabot | {the_date_formatted}", icon_url="https://i.imgur.com/wE5DmmZ.png")
                embed.set_author(name=f"COVID-19 statistics | {countries[3][0]} ({countries[4][0]})", icon_url=f"https://www.countryflags.io/{countries[4][0]}/flat/64.png")

                embed.add_field(name=name_list[0], value=f"{countries[0][0]}", inline=True)
                embed.add_field(name=name_list[1], value=f"{countries[1][0]}", inline=True)
                embed.add_field(name=name_list[2], value=f"{countries[2][0]}", inline=True)
                embed.add_field(name=name_list[3], value=f"**{format(the_stats[0], ',d')}**", inline=True)
                embed.add_field(name=name_list[4], value=f"**{round(the_stats[1], 1)}**%", inline=True)
                embed.add_field(name=name_list[5], value=f"**{round(the_stats[2], 1)}**%", inline=True)

                with open(f"./{graph_file_name}.png", "rb") as f:
                    file = io.BytesIO(f.read())
                img = discord.File(file, filename=f"{graph_file_name}.png")

                embed.set_image(url=f"attachment://{graph_file_name}.png")

                # embed.set_thumbnail(url=f"https://www.countryflags.io/{countries[4][0]}/flat/32.png")

                embed.set_footer(text="Data from Johns Hopkins CSSE")

                msg = await ctx.send(embed=embed, file=img)

                msg_info.append(
                    {
                        "MessageID": msg.id,
                        "MessageObj": msg,
                        "MessageAuthor": ctx.author.id,
                        "Context": ctx,
                        "CountryName": countries[3][0],
                        "CountryCode": countries[4][0],
                        "Date": the_date_formatted,
                        "Cases": cases,
                        "Deaths": deaths,
                        "Recovered": recovered,
                        "CasesFormatted": f"{countries[0][0]}",
                        "DeathsFormatted": f"{countries[1][0]}",
                        "RecoveredFormatted": f"{countries[2][0]}",
                        "Active": the_stats[0],
                        "MortalityRate": the_stats[1],
                        "RecoveryRate": the_stats[2],
                        "CountryCount": "single",
                        "GraphType": "linear",
                        "Timestamp": timestamp
                    }
                )

                # plt.clf()
                os.remove(f"./{graph_file_name}.png")

                # await msg.add_reaction(reactions[1])
                await msg.add_reaction(reactions[2])
                await msg.add_reaction(reactions[3])
                await msg.add_reaction(reactions[0])

        elif len(countries[0]) > country_limit:
            embed = discord.Embed(
                description="This feature supports up to 6 countries. To view the list of available countries use `.list`.",
                timestamp=datetime.utcnow(),
                colour=discord.Color.dark_blue()
            )
            embed.set_author(name="Coronabot | Too many countries!", icon_url="https://i.imgur.com/wE5DmmZ.png")

            msg = await ctx.send(embed=embed)

            msg_info.append(
                {
                    "MessageID": msg.id,
                    "MessageObj": msg,
                    "MessageAuthor": ctx.author.id,
                    "Context": ctx,
                    "Timestamp": timestamp
                }
            )

            await msg.add_reaction(reactions[0])

        elif len(countries[0]) >= len(countries[5]):

            graph_maker_list(countries[4], graph_file_name)
            # compile_flags(countries[4], graph_file_name)

            cases_per_mil = []
            deaths_per_mil = []

            embed = discord.Embed(
                description=descriptions[6],
                timestamp=datetime.utcnow(),
                colour=discord.Color.blue()
            )
            embed.set_author(name="Compare COVID-19 statistics (Cases/1M pop.)", icon_url="https://i.imgur.com/wE5DmmZ.png")

            for I in range(0, len(countries[4])):
                embed.add_field(name=f":flag_{countries[4][I].lower()}: {countries[3][I]} ({countries[4][I]})", value="**{:,.1f}** C/1M".format(
                    per_mil_calculator(countries[3][I], countries[6][3 * (I + 1) - 3])), inline=True)
                cases_per_mil.append(per_mil_calculator(countries[3][I], countries[6][3 * (I + 1) - 3]))
                deaths_per_mil.append(per_mil_calculator(countries[3][I], countries[6][3 * (I + 1) - 2]))

            with open(f"./{graph_file_name}.png", "rb") as f:
                file = io.BytesIO(f.read())
            img = discord.File(file, filename=f"{graph_file_name}.png")

            embed.set_image(url=f"attachment://{graph_file_name}.png")

            # with open(f"./{graph_file_name}compiled_flags.png", "rb") as k:
            #     flags_file = io.BytesIO(k.read())
            # flags_img = discord.File(flags_file, filename=f"{graph_file_name}compiled_flags.png")

            # embed.set_thumbnail(url=f"attachment://{graph_file_name}compiled_flags.png")

            embed.set_footer(text="Data from Johns Hopkins CSSE")

            # msg = await ctx.send(embed=embed, files=[img, flags_img])
            msg = await ctx.send(embed=embed, file=img)

            msg_info.append(
                {
                    "MessageID": msg.id,
                    "MessageObj": msg,
                    "MessageAuthor": ctx.author.id,
                    "Context": ctx,
                    "CountryName": countries[3],
                    "CountryCode": countries[4],
                    "Date": the_date_formatted,
                    "Cases": cases_per_mil,
                    "Deaths": deaths_per_mil,
                    "CountryCount": "multiple",
                    "GraphType": "linear",
                    "StatusType": "confirmed",
                    "Timestamp": timestamp
                }
            )

            # plt.clf()
            os.remove(f"./{graph_file_name}.png")
            # os.remove(f"./{graph_file_name}compiled_flags.png")

            # await msg.add_reaction(reactions[1])
            await msg.add_reaction(reactions[2])
            await msg.add_reaction(reactions[3])
            # await msg.add_reaction(reactions[4])
            await msg.add_reaction(reactions[5])
            await msg.add_reaction(reactions[0])

            # message_authors.update({str(msg.id): ctx.author.id})

        if len(countries[5]) != 0:
            error_list = ""

            for i in range(0, len(countries[5])):
                if i == (len(countries[5]) - 1):
                    error_list += "**" + str(countries[5][i]) + "**"
                else:
                    error_list += "**" + str(countries[5][i]) + "**" + ", "

            if len(countries[5]) == 1:
                embed = discord.Embed(
                    description="No record of this country: {}\n\nUse `.list` to view the list of available countries.".format(error_list),
                    timestamp=datetime.utcnow(),
                    colour=discord.Color.blue()
                )
            else:
                embed = discord.Embed(
                    description="No record of these countries: {}\n\nUse `.list` to view the list of available countries.".format(error_list),
                    timestamp=datetime.utcnow(),
                    colour=discord.Color.blue()
                )

            embed.set_author(name="Coronabot | Error 404", icon_url="https://i.imgur.com/wE5DmmZ.png")

            embed.set_thumbnail(url="https://i.imgur.com/DoUZwiU.png")

            # embed.add_field(name="Help", value="Use `.list` to view the list of available countries.")

            msg = await ctx.send(embed=embed)

            msg_info.append(
                {
                    "MessageID": msg.id,
                    "MessageObj": msg,
                    "MessageAuthor": ctx.author.id,
                    "Context": ctx,
                    "Timestamp": timestamp
                }
            )

            await msg.add_reaction(reactions[0])


queue = []


@bot.command()
# @commands.cooldown(1, 2, type=commands.BucketType.default)
async def stats(ctx, *entries):
    queue.append({"Context": ctx, "ContextID": ctx.message.id, "Entries": entries})

    tasks = []

    for i in range(0, len(queue)):
        task = asyncio.create_task(make_stats_embed(queue[i]["Context"], queue[i]["Entries"], queue[i]["ContextID"]))
        tasks.append(task)

    queue.clear()
    await asyncio.gather(*tasks)


@bot.command()
async def list(ctx):
    country_list = ""

    for i in range(0, (len(country_data))):
        country_list += str(country_data[i]["Code"]) + ": " + str(country_data[i]["Name"]) + "\n"
        if len(country_list) >= 1900:
            await ctx.author.send("```" + country_list + "```")
            country_list = ""


@bot.command()
async def help(ctx):
    remove_messages()

    today = datetime.today()
    timestamp = today.timestamp()

    embed = discord.Embed(
        color=discord.Color.blue()
    )
    embed.set_author(name="Coronabot | Cheat-sheet", icon_url="https://i.imgur.com/wE5DmmZ.png")

    embed.set_thumbnail(url="https://i.imgur.com/LpTun0d.png")

    embed.add_field(name="`.help`", value="Shows this **cheat-sheet**.", inline=False)
    embed.add_field(name="`.list`",
                    value="Sends a direct message to the author with the list of available **country codes**.",
                    inline=False)
    embed.add_field(name="`.stats <country-name(s)/code(s)>` (up to 6 countries)",
                    value="Returns the current COVID-19 **statistics** of the specified country.\n• Entering **multiple** countries (up to 6) will show a graph that compares **cases**/**deaths** per 1 million population.\n• If no countries are given, then the bot will return the **global** COVID-19 statistics.",
                    inline=False)
    embed.add_field(
        name="Reactions",
        value=f"{reactions[0]} → **Deletes** the bot's message.\n\n{reactions[1]} → Sends a **linear** graph.\n\n{reactions[2]} → Sends a **logarithmic** graph.\n\n{reactions[3]} → Sends a **bar** chart.\n\n{reactions[4]} → Changes data to **Cases**/1M population.\n\n{reactions[5]} → Changes data to **Deaths**/1M population."
    )

    embed.set_footer(
        text="NOTE: Country names with two or more parts must be connected with a dash (-). (e.g. united-kingdom, united-states, etc.)"
    )

    msg = await ctx.send(embed=embed)

    msg_info.append(
        {
            "MessageID": msg.id,
            "MessageObj": msg,
            "MessageAuthor": ctx.author.id,
            "Context": ctx,
            "Timestamp": timestamp
        }
    )

    await msg.add_reaction(reactions[0])


with open('config.json') as config:
    data = json.load(config)

token = data["Token"]

bot.run(token)
