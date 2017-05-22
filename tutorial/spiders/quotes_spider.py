#coding=utf-8
import logging  
import re  
import sys  
import scrapy  
from scrapy.spiders import CrawlSpider, Rule  
from scrapy.linkextractors import LinkExtractor  
from scrapy.http import Request, FormRequest, HtmlResponse  


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        urls = [
            'http://quotes.toscrape.com/page/1/',
            'http://quotes.toscrape.com/page/2/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
        
class AuthorSpider(scrapy.Spider):
    name = 'author'
    start_urls = ['http://quotes.toscrape.com/']
    def parse(self, response):
        response.xpath("//input[@name='authenticity_token']/@value").extract()

        # follow links to author pages
        for href in response.css('small.author + a::attr(href)').extract():
            yield scrapy.Request(response.urljoin(href),
                                 callback=self.parse_author)

        # follow pagination links
        next_page = response.css('.next a::attr(href)').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
            
    def parse_author(self, response):
        def extract_with_css(query):
            return response.css(query).extract_first().strip()
        yield {
            'name': extract_with_css('h3.author-title::text'),
#             'birthdate': extract_with_css('span.author-born-date::text'),
#             'bio': extract_with_css('.author-description::text'),
#             'location': extract_with_css('.author-born-location::text'),
        }

class GithubSpider(scrapy.Spider):
    name = "github"
    def after_login(self, response):  
        self.logger.info(response.meta)
#         self.logger.info(request.headers)
        for url in self.start_urls:  
            # 因为我们上面定义了Rule，所以只需要简单的生成初始爬取Request即可  
            yield Request(url, meta={'cookiejar': response.meta['cookiejar']}) 

    def post_login(self, response):  
# 先去拿隐藏的表单参数authenticity_token  
        authenticity_token = response.xpath(  
            '//input[@name="authenticity_token"]/@value').extract_first()  
        self.logger.info('authenticity_token=' + authenticity_token)  
        return [FormRequest.from_response(response,  
                                  url='https://github.com/session',  
                                  meta={'cookiejar': response.meta['cookiejar']},  
#                                   headers=self.post_headers,  # 注意此处的headers  
                                  formdata={  
                                      'utf8': '✓',  
                                      'login': 'eisscerav',  
                                      'password': 'fanxin81102x',  
                                      'authenticity_token': authenticity_token  
                                  },  
                                  callback=self.after_login,  
                                  dont_filter=True  
                                  )]
#     start_urls = [r"https://github.com/login"]
    def start_requests(self):  
        yield Request(r"https://github.com/login",  
                      meta={'cookiejar': 1}, 
                      callback=self.post_login)
#     def parse(self, response):
#         token = response.xpath("//input[@name='authenticity_token']/@value").extract_first()
#         self.logger.info(token)
#         self.logger.info(self.request.headers)
        


        

