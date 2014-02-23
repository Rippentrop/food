'''
Parsing restaurant web data goes here
'''
import re
import json

from bs4 import BeautifulSoup, Tag

from common import *
from config import *


def parse_food_data(data):
    unica_menu = dict()
    for restaurant, week_html in data['unica'].items():
        unica_menu[restaurant] = parse_unica_html(week_html)

    sodexo_menu = dict()
    for restaurant, week_json in data['sodexo'].items():
        sodexo_menu[restaurant] = parse_sodexo_json(week_json)

    return { 'sodexo': sodexo_menu, 'unica': unica_menu }


def parse_unica_html(html):
    parser = BeautifulSoup(html)
    html_menu = parser.find_all('div', {'class': 'accord'})

    week_menu = dict()

    for day in html_menu:

        day_of_week = int(day.h4['data-dayofweek'])
        day_menu = list()

        for food in day.table('tr'):

            try:
                # Filter out non-tags
                only_tags = (food_tag for food_tag in food if isinstance(food_tag, Tag))
                food = Food()
                for tag in only_tags:

                    if 'lunch' in tag['class']:
                        food.name = tag.string

                    # Food properties like VEG, G or L
                    if 'limitations' in tag['class']:
                        for limit in tag.stripped_strings:
                            limit = limit
                            if limit == '/':
                                food.properties.append('/')
                            elif limit:
                                food.properties.append(limit)

                    if 'price' in tag['class']:
                        food.prices = re.findall('\d,\d\d', tag.string)

                day_menu.append(food)

            except:
                pass

        week_menu[day_of_week] = day_menu

    return week_menu


def parse_sodexo_json(week_json):
    week = [json.loads(day) for day in week_json]

    week_menu = dict()
    for day_of_week, day in enumerate(week):
        day_menu = list()

        if not day['courses']: # Skip empty days
            continue

        for food_data in day['courses']:
            try:
                food = Food()
                if LANG.lower() == 'en':
                    food.name = food_data['title_en']
                else:
                    food.name = food_data['title_fi']

                food.prices = re.findall('\d,\d\d', food_data['price'])
                food.properties = [prop.strip() for prop in food_data['properties'].split(',')]
                if food_data['category'].lower() == 'kasvislounas':
                    food.properties.append('VEG')
                
                day_menu.append(food)

            except:
                pass # This is for when days run out, usually on saturday.

        week_menu[day_of_week] = day_menu

    return week_menu
