# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class DilegoPipeline(object):
    def process_item(self, item, spider):
        return item

from scrapy import signals
from scrapy.contrib.exporter import CsvItemExporter


class CSVPipeline(object):

    def __init__(self):
        self.files = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        if spider.name == 'dilego_category':
            file1 = open('crawler categories.csv', 'w+b')
            self.files[spider] = file1
            self.exporter = CsvItemExporter(file1)
            self.exporter.fields_to_export = ['Category_Name', 'Category_Parents', 'Meta_Title', 'Meta_Description', 'Category_URL']
        if spider.name == 'dilego_product':
            file2 = open('crawler products.csv', 'w+b')
            self.files[spider] = file2
            self.exporter = CsvItemExporter(file2)
            self.exporter.fields_to_export = ['Product_Name', 'Product_Parent_categories', 'Product_Short_Description', 'Product_Long_Description', 'Technical_information', 'Contents_Included', 'Product_Price', 'Supplier_Reference', 'Stock_Status', 'Meta_Title', 'Meta_Keywords', 'Meta_Description', 'Cover_Image_Url', 'Thumb_Images_Url']
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
