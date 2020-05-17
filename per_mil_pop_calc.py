import json


def per_mil_calculator(name, cases):

    with open("country_populations.json") as json_file:
        data = json.load(json_file)

    pop_data = list(filter(lambda find_pop: find_pop["Country"] in name, data))

    per_mil_pop = (cases*1000000)/pop_data[0]["Population"]

    return round(per_mil_pop, 1)
