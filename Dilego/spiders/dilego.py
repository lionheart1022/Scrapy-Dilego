#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy
import re
from scrapy import Request, Selector
import requests

from Dilego.items import CategoryItem, ProductItem
from HTMLParser import HTMLParser

is_empty = lambda x, y=None: x[0] if x else y


class CategorySpider(scrapy.Spider):
    name = "dilego_category"
    allowed_domains = ["http://www.dilego.de/"]

    start_urls = ['http://www.dilego.de/catalog/seo_sitemap/category/']

    HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/58.0.3029.96 Safari/537.36"}

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse_pages)

    def parse_pages(self, response):
        total_match = response.xpath('//div[@class="pager"]/p[@class="amount"]/text()').extract()
        if total_match:
            page_links = []
            total_match = re.search('(\d+) gesamt', total_match[0])
            if total_match:
                total_match = total_match.group(1)
                page_count = int(total_match) / 50
                if page_count * 25 < total_match:
                    page_count += 1
                for i in range(1, page_count+1):
                    page_link = response.url + '?p=' + str(i)
                    page_links.append(page_link)
                for page_link in page_links:
                    yield scrapy.Request(url=page_link, callback=self.parse_links,
                                         headers=self.HEADERS, dont_filter=True)
        else:
            yield scrapy.Request(url=response.url, callback=self.parse_links,
                                 headers=self.HEADERS, dont_filter=True)

    def parse_links(self, response):
        links = response.xpath('//ul[@class="sitemap"]/li/a/@href').extract()
        for link in list(set(links)):
            yield scrapy.Request(url=link, callback=self.parse_page,
                                 headers=self.HEADERS, dont_filter=True)

    @staticmethod
    def parse_page(response):
        category = CategoryItem()

        if response.xpath('//p[@class="note-msg"]'):
            return

        category['Category_Name'] = response.xpath('//div[@class="breadcrumbs"]/ul/li/strong//text()')[0].extract()

        categories = response.xpath('//div[@class="breadcrumbs"]/ul/li[not(contains(@class, "home"))]'
                                    '/a/text()').extract()
        if categories:
            if len(categories) == 1:
                category['Category_Parents'] = categories[0]
            if len(categories) == 2:
                category['Category_Parents'] = categories[1] + ', ' + categories[0]
        else:
            category['Category_Parents'] = 'Home'

        category['Meta_Title'] = response.xpath('//title/text()')[0].extract()

        category['Meta_Description'] = HTMLParser().unescape(response.xpath('//meta[@name="description"]'
                                                                            '/@content')[0].extract())

        category['Category_URL'] = response.url

        return category


class ProductSpider(scrapy.Spider):
    name = "dilego_product"
    allowed_domains = ["www.dilego.de"]

    start_urls = ['http://www.dilego.de/catalog/seo_sitemap/category/']

    HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                             "Chrome/58.0.3029.96 Safari/537.36"}

    AUTH_URL = 'https://www.dilego.de/customer/account/login/'

    AUTH_HEADERS = {
        'Content-Type': 'application/x-www-form-urlen'
                        'coded',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/58.0.3029.110 Safari/537.36'
    }

    def __init__(self, *args, **kwargs):
        super(ProductSpider, self).__init__(
            site_name=self.allowed_domains[0], *args, **kwargs)

        self.login = kwargs.get("login", "kundtjanst@shop4you.se")
        self.password = kwargs.get("password", "shop4youjuli2017")

    def start_requests(self):
        s = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=3)
        b = requests.adapters.HTTPAdapter(max_retries=3)
        s.mount('http://', a)
        s.mount('https://', b)
        body = '{{"login": {{"username": "{email}", "password": "{password}"}}, '.format(email=self.login,
                                                                                         password=self.password)
        with requests.Session() as s:
            # Set auth cookies
            s.get(
                self.AUTH_URL,
                data=body,
                headers=self.AUTH_HEADERS,
                timeout=5
            )
            # An authorised request.
            response = s.post(
                self.start_urls[0],
                headers=self.AUTH_HEADERS,
                timeout=5
            )
            response = response.text

            total_match = Selector(text=response).xpath('//div[@class="pager"]/p[@class="amount"]/text()').extract()
            if total_match:
                page_links = []
                total_match = re.search('(\d+) gesamt', total_match[0])
                if total_match:
                    total_match = total_match.group(1)
                    page_count = int(total_match) / 50
                    if page_count * 25 < total_match:
                        page_count += 1
                    for i in range(1, page_count+1):
                        page_link = self.start_urls[0] + '?p=' + str(i)
                        page_links.append(page_link)
                    for page_link in page_links:
                        yield scrapy.Request(url=page_link, callback=self.parse_links,
                                             headers=self.HEADERS, dont_filter=True)
            else:
                yield scrapy.Request(url=self.start_urls[0], callback=self.parse_links,
                                     headers=self.HEADERS, dont_filter=True)

    def parse_links(self, response):
        links = response.xpath('//ul[@class="sitemap"]/li/a/@href').extract()
        for link in list(set(links)):
            yield scrapy.Request(url=link, callback=self.parse_pages,
                                 headers=self.HEADERS, dont_filter=True)

    def parse_pages(self, response):
        if response.xpath('//p[@class="note-msg"]'):
            return
        total_match = response.xpath('//div[@class="pager"]/p[@class="amount"]/text()').extract()
        if total_match:
            page_links = []
            total_match = re.search('(\d+) gesamt', total_match[0])
            if total_match:
                total_match = total_match.group(1)
                page_count = int(total_match) / 25
                if page_count * 25 < total_match:
                    page_count += 1
                for i in range(1, page_count+1):
                    page_link = response.url + '?p=' + str(i)
                    page_links.append(page_link)
                for page_link in page_links:
                    yield scrapy.Request(url=page_link, callback=self.parse_link,
                                         headers=self.HEADERS, dont_filter=True)
        else:
            yield scrapy.Request(url=response.url, callback=self.parse_link,
                                 headers=self.HEADERS, dont_filter=True)

    def parse_link(self, response):
        links = response.xpath('//div[@class="products-list"]/div[contains(@class, "item")]'
                               '/div[@class="product-shop"]//h2[@class="product-name"]'
                               '/a/@href').extract()
        for link in list(set(links)):
            yield scrapy.Request(url=link, callback=self.parse_product,
                                 headers=self.HEADERS, dont_filter=True)

    @staticmethod
    def parse_product(response):
        product = ProductItem()

        product_name = response.xpath('//title/text()')[0].extract().strip()
        product['Product_Name'] = product_name

        category_list = ''
        categories = response.xpath('//div[@class="breadcrumbs"]/ul/li[not(contains(@class, "home"))]'
                                    '/a/text()').extract()
        for category_name in categories:
            if category_name == categories[-1]:
                category_list += category_name
            else:
                category_list += category_name + ', '
        product['Product_Parent_categories'] = category_list

        technical_list = []
        technical_information = ''
        technical_info = response.xpath('//div[@id="content_tab_02"]/ul/li/text()').extract()
        for technical in technical_info:
            if not technical.strip() == '':
                technical_list.append(technical.strip())
        for tech in technical_list:
            if tech == technical_list[-1]:
                technical_information += tech
            else:
                technical_information += tech + '__'
        product['Technical_information'] = technical_information

        contents_list = []
        contents_info = response.xpath('//div[@id="content_tab_03"]/li/text()').extract()
        for content in contents_info:
            if not content.strip() == '':
                contents_list.append(content.strip())
        product['Contents_Included'] = contents_list

        product['Product_Short_Description'] = response.xpath('//meta[@name="description"]/@content')[0].extract()

        long_description_list = []
        long_description = response.xpath('//div[@class="short-description"]'
                                          '//text()').extract()
        for long_desc in long_description:
            if not long_desc.strip() == '':
                long_description_list.append(long_desc.strip())
        product['Product_Long_Description'] = "".join(long_description_list)

        product['Product_Price'] = response.xpath('//div[@class="product-essential"]'
                                                  '//div[@class="price-box"]'
                                                  '/span[@class="regular-price"]/span/text()')[0].extract().strip()

        product['Supplier_Reference'] = re.search('Artikelnummer:</b> (.*)</div>', response.body).group(1)

        product['Meta_Title'] = response.xpath('//title/text()')[0].extract().strip()

        product['Meta_Keywords'] = response.xpath('//meta[@name="keywords"]/@content')[0].extract().strip()

        product['Meta_Description'] = response.xpath('//meta[@name="description"]/@content')[0].extract().strip()

        image_urls = response.xpath('//div[@class="product-view"]//table//td/img/@src').extract()
        product['Cover_Image_Url'] = image_urls[0]

        image_urls = image_urls[1:]
        image_list = []
        for image_url in image_urls:
            image_url = image_url.replace('_thumb', '')
            image_list.append(image_url)
        product['Thumb_Images_Url'] = image_list

        stock = response.xpath('//p[contains(@class, "availability")]/span/text()')[0].extract()
        if 'Auf Lager' in stock:
            product['Stock_Status'] = 'In Stock'
        else:
            product['Stock_Status'] = 'Out of Stock'

        yield product