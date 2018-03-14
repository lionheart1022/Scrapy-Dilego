# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CategoryItem(scrapy.Item):
    # define the fields for your item here like:
    Category_Name = scrapy.Field()
    Category_Parents = scrapy.Field()
    Meta_Title = scrapy.Field()
    Meta_Description = scrapy.Field()
    Image_Url = scrapy.Field()
    Category_URL = scrapy.Field()


class ProductItem(scrapy.Item):
    # define the fields for your item here like:
    Product_Name = scrapy.Field()
    Product_Parent_categories = scrapy.Field()
    Product_Short_Description = scrapy.Field()
    Product_Long_Description = scrapy.Field()
    Technical_information = scrapy.Field()
    Contents_Included = scrapy.Field()
    Product_Price = scrapy.Field()
    Product_Variants = scrapy.Field()
    Supplier_Reference = scrapy.Field()
    Meta_Title = scrapy.Field()
    Meta_Keywords = scrapy.Field()
    Meta_Description = scrapy.Field()
    Cover_Image_Url = scrapy.Field()
    Thumb_Images_Url = scrapy.Field()
    Stock_Status = scrapy.Field()