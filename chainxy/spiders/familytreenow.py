# from __future__ import unicode_literals
import scrapy

import json

import os

import scrapy

from scrapy.spiders import Spider

from scrapy.http import FormRequest

from scrapy.http import Request

from chainxy.items import ChainItem

from lxml import etree

from lxml import html

import pdb

import random



class familytreenow(scrapy.Spider):

	handle_httpstatus_list = [403] 

	name = 'familytreenow'

	domain = 'https://www.familytreenow.com'

	history = []

	proxy_list = []

	headers = {
			"accept": "text/html, application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
			"upgrade-insecure-requests": "1",
			"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
		}


	def __init__(self):

		script_dir = os.path.dirname(__file__)

		file_path = script_dir + '/proxies.txt'

		with open(file_path, 'rb') as text:

			self.proxy_list =  [ "http://" + x.strip() for x in text.readlines()]

	
	def start_requests(self):

		yield scrapy.Request(url=self.domain, callback=self.parse_alpha_list, headers=self.headers, meta={'proxy': random.choice(self.proxy_list)}, dont_filter=True) 

		# url = "https://www.familytreenow.com/search/genealogy/results?first=John&last=Anderson"

		# yield scrapy.Request(url=url, callback=self.parse_result_list, headers=self.headers, meta={'proxy': random.choice(self.proxy_list)}, dont_filter=True) 


	def parse_alpha_list(self, response):

		if response.status == 403:

			yield scrapy.Request(url=response.url, callback=self.parse_alpha_list, headers=self.headers, meta={'proxy': random.choice(self.proxy_list)}, dont_filter=True)

		else:

			alpha_list = response.xpath('//div[contains(@class, "footer text-center")]//p[@class="small text-center"]//a/@href').extract()

			for alpha in alpha_list:

				link = self.domain + alpha

				yield scrapy.Request(url=link, callback=self.parse_first_name, headers=self.headers, meta={'proxy': random.choice(self.proxy_list)}, dont_filter=True) 


	def parse_first_name_page_list(self, response):

		if response.status == 403:

			yield scrapy.Request(url=response.url, callback=self.parse_first_name_page_list, headers=self.headers, meta={'proxy': random.choice(self.proxy_list)}, dont_filter=True)

		else:

			p_check = response.xpath('//p')

			for p in p_check:

				if 'page' in ''.join(p.xpath('.//text()').extract()).lower():

					page_list = p.xpath('//a//@href').extract()

					for page in page_list:

						link = self.domain + page

						yield scrapy.Request(url=link, callback=self.parse_first_name, headers=self.headers, meta={'proxy': random.choice(self.proxy_list)}, dont_filter=True) 


	def parse_first_name(self, response):

		if response.status == 403:

			yield scrapy.Request(url=response.url, callback=self.parse_first_name, headers=self.headers, meta={'proxy': random.choice(self.proxy_list)}, dont_filter=True)

		else:

			first_name_list = response.xpath('//table[contains(@class, "table table-condensed")]//a/@href').extract()

			for first_name in first_name_list:

				link = self.domain + first_name

				yield scrapy.Request(url=link, callback=self.parse_full_name_page_list, headers=self.headers, meta={'proxy': random.choice(self.proxy_list)}, dont_filter=True) 


	def parse_full_name_page_list(self, response):

		if response.status == 403:

			yield scrapy.Request(url=response.url, callback=self.parse_full_name_page_list, headers=self.headers, meta={'proxy': random.choice(self.proxy_list)}, dont_filter=True)

		else:

			p_check = response.xpath('//p')

			for p in p_check:

				if 'page' in ''.join(p.xpath('.//text()').extract()).lower():

					page_list = p.xpath('//a//@href').extract()

					for page in page_list:

						link = self.domain + page

						yield scrapy.Request(url=link, callback=self.parse_full_name, headers=self.headers, meta={'proxy': random.choice(self.proxy_list)}, dont_filter=True) 


	def parse_full_name(self, response):

		if response.status == 403:

			yield scrapy.Request(url=response.url, callback=self.parse_full_name, headers=self.headers, meta={'proxy': random.choice(self.proxy_list)}, dont_filter=True)

		else:

			full_name_list = response.xpath('//table[contains(@class, "table table-condensed")]//a/@href').extract()

			for full_name in full_name_list:

				splited_name = full_name.split('/')

				link = "https://www.familytreenow.com/search/genealogy/results?first=" + splited_name[-1] + '&last=' + splited_name[-2]

				yield scrapy.Request(url=link, callback=self.parse_result_list, headers=self.headers, meta={'proxy': random.choice(self.proxy_list)}, dont_filter=True) 

	
	def parse_result_list(self, response):

		if response.status == 403:

			yield scrapy.Request(url=response.url, callback=self.parse_result_list, headers=self.headers, meta={'proxy': random.choice(self.proxy_list)}, dont_filter=True)

		else:

			result_list = response.xpath('//table[contains(@id, "summaryResults")]//a[contains(@class, "summary-detail-link detail-link")]/@href').extract()

			for result in result_list:

				link = self.domain + result

				yield scrapy.Request(url=link, callback=self.parse_detail, headers=self.headers, meta={'proxy': random.choice(self.proxy_list)}, dont_filter=True) 

			next_page = response.xpath('//a[contains(@id, "btnNextPage")]/@href').extract_first()

			if next_page:

				link = self.domain + next_page

				yield scrapy.Request(url=link, callback=self.parse_result_list, headers=self.headers, meta={'proxy': random.choice(self.proxy_list)}, dont_filter=True) 


	def parse_detail(self, response):

		if response.status == 403:

			yield scrapy.Request(url=response.url, callback=self.parse_detail, headers=self.headers, meta={'proxy': random.choice(self.proxy_list)}, dont_filter=True)

		else:

			item = ChainItem()

			detail = response.xpath('//table[contains(@class, "table table-condensed")]')[0].xpath('.//tr')

			try:

				item['name'] = ' '.join(self.eliminate_space(detail[0].xpath('.//text()').extract())[1:])

				detail = self.eliminate_space(response.xpath('//table[contains(@class, "table table-condensed")]')[0].xpath('.//tr//text()').extract())

				for idx, val in enumerate(detail):

					try:

						if 'birth year' in val.lower():

							item['birth_year'] = detail[idx+1]

						if 'age' in val.lower():

							item['age'] = detail[idx+1]

					except Exception as e:

						pass


			except Exception as e:

				pass

			bulk_list = response.xpath('//div[@class="panel panel-primary"]')


			for bulk in bulk_list:
				
				check = ''.join(bulk.xpath('.//div[@class="panel-heading text-center"]//text()').extract())
	
				if 'relative' in check.lower():
					
					record_list = bulk.xpath('.//table[contains(@class, "table table-condensed table-striped")]//tr')

					temp = '  '

					for record in record_list[1:]:

						try:

							name = self.validate(''.join(record.xpath('.//td[1]//text()').extract()))

							age = self.validate(''.join(record.xpath('.//td[2]//text()').extract()))

							birth_year = self.validate(''.join(record.xpath('.//td[3]//text()').extract()))

							temp += name

							if birth_year != '':

								if age == '':

									age = str( 2018 - int(birth_year))

								temp += ', ' + age + ', ' + birth_year

							temp += ' | '

						except Exception as e:

							pass

					item['possible_relatives'] = temp[:-2].strip()

				if 'possible associates' in check.lower():

					record_list = bulk.xpath('.//table[contains(@class, "table table-condensed table-striped")]//tr')

					temp = '  '

					for record in record_list[1:]:

						try:

							name = self.validate(''.join(record.xpath('.//td[1]//text()').extract()))

							age = self.validate(''.join(record.xpath('.//td[2]//text()').extract()))

							birth_year = self.validate(''.join(record.xpath('.//td[3]//text()').extract()))

							temp += name

							if birth_year != '':

								if age == '':

									age = str( 2018 - int(birth_year))

								temp += ', ' + age + ', ' + birth_year

							temp += ' | '

						except Exception as e:

							pass

					item['possible_associates'] = temp[:-2].strip()

				if 'address' in check.lower():

					record_list = bulk.xpath('.//table[contains(@class, "table table-condensed table-striped")]//tr')

					temp = '  '

					for record in record_list[1:]:

						try:

							temp += self.validate(' '.join(self.eliminate_space(record.xpath('.//text()').extract())))

							temp += ' | '

						except Exception as e:

							pass

					item['addresses'] = temp[:-2].strip()

				if 'phone' in check.lower():

					record_list = bulk.xpath('.//table[contains(@class, "table table-condensed table-striped")]//tr')

					temp = '  '

					for record in record_list[1:]:

						try:

							temp += self.validate(' : '.join(self.eliminate_space(record.xpath('.//text()').extract())))

							temp += ' | '

						except Exception as e:

							pass

					item['phone_numbers'] = temp[:-2].strip()

			item['link'] = response.url

			yield item


	def validate(self, item):

		try:

			return item.replace('\n', '').replace('\t','').replace('\r', '').encode('ascii','ignore').strip()

		except:

			pass


	def eliminate_space(self, items):

	    tmp = []

	    for item in items:

	        if self.validate(item) != '':

	            tmp.append(self.validate(item))

	    return tmp