# import requests
#
# # https://stackoverflow.com/questions/8653516/python-list-of-dictionaries-search
#
# url_sum = "https://api.covid19api.com/summary"
# response_sum = requests.get(url_sum)
# data_sum = response_sum.json()


def get_stats(data, country_list=None):

    country_list = list(country_list)

    country_list_slugs = []
    country_list_codes = []
    error_lst = []

    cases = []
    new_cases = []

    deaths = []
    new_deaths = []

    recovered = []
    new_recovered = []

    names = []
    codes = []

    stats = []

    if not country_list:

        cases.append(data["Global"]["TotalConfirmed"])
        new_cases.append(data["Global"]["NewConfirmed"])

        deaths.append(data["Global"]["TotalDeaths"])
        new_deaths.append(data["Global"]["NewDeaths"])

        recovered.append(data["Global"]["TotalRecovered"])
        new_recovered.append(data["Global"]["NewRecovered"])

        stats.append(cases)
        stats.append(deaths)
        stats.append(recovered)

        if new_cases != 0:
            cases = format(int(cases[0]), ",d") + " (+" + format(int(new_cases[0]), ",d") + ")"

        if new_deaths != 0:
            deaths = format(int(deaths[0]), ",d") + " (+" + format(int(new_deaths[0]), ",d") + ")"

        if new_recovered != 0:
            recovered = format(int(recovered[0]), ",d") + " (+" + format(int(new_recovered[0]), ",d") + ")"

    else:
        for i in range(0, len(country_list)):
            if len(country_list[i]) > 2:
                country_list[i] = country_list[i].lower()
            else:
                country_list[i] = country_list[i].upper()

        # print(country_list)

        slug = list(filter(lambda change_name: change_name["Slug"] in country_list, data["Countries"]))
        for i in range(0, len(slug)):
            country_list_codes.append(slug[i]["CountryCode"])
            country_list_slugs.append(slug[i]["Slug"])
        # print(country_list_codes, country_list_slugs)

        code = list(filter(lambda change_name: change_name["CountryCode"] in country_list, data["Countries"]))
        for i in range(0, len(code)):
            country_list_codes.append(code[i]["CountryCode"])
            country_list_slugs.append(code[i]["Slug"])
        # print(country_list_codes, country_list_slugs)

        # print(slug)
        # print(code)

        for i in range(0, len(country_list)):
            if str.upper(country_list[i]) not in country_list_codes and str.lower(country_list[i]) not in country_list_slugs:
                # print(str.upper(country_list[i]))
                error_lst.append(country_list[i])

        # print(error_lst)

        for i in range(0, len(error_lst)):
            country_list.remove(error_lst[i])

        # for i in range(0, len(slug)):
        #     if len(country_list[i]) > 2:
        #         country_list[i] = slug[i]["CountryCode"]
        #     else:
        #         country_list[i] = country_list[i].upper()

        # lst = list(filter(lambda get_countries: get_countries["CountryCode"] in country_list, data["Countries"]))
        lst = slug + code
        # print(lst)

        for i in range(0, len(lst)):
            cases.append(lst[i]["TotalConfirmed"])
            new_cases.append(lst[i]["NewConfirmed"])

            deaths.append(lst[i]["TotalDeaths"])
            new_deaths.append(lst[i]["NewDeaths"])

            recovered.append(lst[i]["TotalRecovered"])
            new_recovered.append(lst[i]["NewRecovered"])

            names.append(lst[i]["Country"])
            codes.append(lst[i]["CountryCode"])

            stats.append(lst[i]["TotalConfirmed"])
            stats.append(lst[i]["TotalDeaths"])
            stats.append(lst[i]["TotalRecovered"])

            if new_cases[i] != 0:
                cases[i] = format(int(cases[i]), ",d") + " (+" + format(int(new_cases[i]), ",d") + ")"

            if new_deaths[i] != 0:
                deaths[i] = format(int(deaths[i]), ",d") + " (+" + format(int(new_deaths[i]), ",d") + ")"

            if new_recovered[i] != 0:
                recovered[i] = format(int(recovered[i]), ",d") + " (+" + format(int(new_recovered[i]), ",d") + ")"

    return cases, deaths, recovered, names, codes, error_lst, stats


# # the_list = ["hello there", "united-kingdom", "germany", "youtube", "switzerland"]
# # the_list = ["gr", "United-Kingdom", "netherlands", "youtube"]
# the_list = ()
# new_list = get_stats(data_sum, the_list)
# print(new_list)
