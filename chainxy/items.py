# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class ChainItem(Item):

	name = Field()

	age = Field()

	birth_year = Field()

	possible_relatives = Field()

	possible_associates = Field()

	addresses = Field()

	phone_numbers = Field()

	ethnicity = Field()

	link = Field()


