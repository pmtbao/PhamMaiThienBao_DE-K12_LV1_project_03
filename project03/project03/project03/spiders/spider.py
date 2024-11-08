import scrapy
from bs4 import BeautifulSoup as bs
from scrapy.spiders import SitemapSpider
from scrapy.http import XmlResponse
import urllib.request
import time
import random
import base64

class ImagesSpider(SitemapSpider):
	name = "images"
	sitemap_urls = ["https://www.glamira.com/sitemap.xml"]
	sitemap_follow = ['^https://www.glamira.com/media/sitemap/glus/product_image_provider',]
	def parse (self, response):
		images = response.css("div.gallery-main")
		for image in images.css("img"):
			src = image.xpath("@srcset").get().split(", ")[1].split(" ")[0]
			converted_string = ''
			a = urllib.request.urlretrieve(src,'img')
			with open("img", "rb") as image2string:
			    #img to base64
				converted_string = base64.b64encode(image2string.read())
			image2string.close()
			title = image.xpath("@title").get()
			yield {'img' : f"{converted_string}", 'title' : title}
    	
                        

