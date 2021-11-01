import scrapy
import json
from pydispatch import dispatcher
from scrapy import signals

class HemnetSpider(scrapy.Spider):
    name = "hemnet"
    start_urls = ['https://www.hemnet.se/bostader?location_ids%5B%5D=17755&item_types%5B%5D=bostadsratt']
    counter = 0
    results={}

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def parse(self, response):
        #Text Mining
        #We need to get the all ad links with %a::attr('href')% which is inside the %li.normal-results_hit% which is inside %ul.normal-results% 
        for ad in response.css("ul.normal-results > li.normal-results__hit > a::attr('href')"):
            yield scrapy.Request(url=ad.get(), callback=self.parseInnerPage)

        #End of page identification
        #Text Mining
        nextPage = response.css("a.next_page::attr('href')").get()
        if nextPage is not None:
            response.follow(nextPage, self.parse)
    
    def parseInnerPage(self, response):
        #Text Mining
        streetName=response.css("h1.qa-property-heading::text").get()
        price=response.css("p.property-info__price::text").get()
        #Cleaning data
        price = price.replace("kr", "") # Cleaning currency sign
        price = price.replace(u"\xa0", "") #Cleaning White Spaces

        attrData = {}
        for attr in response.css("div.property-attributes > div.property-attributes-table > dl.property-attributes-table__area > div.property-attributes-table__row"):
            attrLabel = attr.css("dt.property-attributes-table__label::text").get() #Text Mining
            if attrLabel is not None:
                attrLabel = attrLabel.replace(u"\n", "")
                attrLabel = attrLabel.replace(u"\t", "")
                attrLabel = attrLabel.strip()

            attrValue = attr.css("dd.property-attributes-table__value::text").get() #Text Mining
            if attrValue is not None:
                attrValue = attrValue.replace(u"\n", "")
                attrValue = attrValue.replace(u"\t", "")
                attrValue = attrValue.strip()
            
            if attrLabel is not None:
                attrData[attrLabel] = attrValue
        
        self.results[self.counter] = {
            "streetName" : streetName,
            "price" : price,
            "attr" : attrData
        }
        self.counter+=1 

    def spider_closed(self,spider):
        with open('results.json', 'w') as fp:
            json.dump(self.results,fp)         