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
    def crawl_myproj(self, response):
        self.logger.info(response.status)
        projects = response.xpath('//div[@class="d-inline-block mb-1"]/h3/a/text()').extract()
        self.logger.info(response.url)
        for proj in projects:
            yield {
                'project': proj.strip(),
            } 
    
    def after_login(self, response):  
        self.logger.info(response.status)
        yield Request(url='https://github.com/eisscerav?tab=repositories',
                      callback=self.crawl_myproj)

    def post_login(self, response):  
# 先去拿隐藏的表单参数authenticity_token  
        authenticity_token = response.xpath(  
            '//input[@name="authenticity_token"]/@value').extract_first()  
        self.logger.info('authenticity_token=' + authenticity_token)  
        return [FormRequest.from_response(response,  
                                  url='https://github.com/session',  
                                  meta={'cookiejar': response.meta['cookiejar']},  
                                  formdata={  
                                      'utf8': '✓',  
                                      'login': 'eisscerav',  
                                      'password': 'fanxin811022',  
                                      'authenticity_token': authenticity_token  
                                  },  
                                  callback=self.after_login,  
#                                   dont_filter=True  
                                  )]
        
    def start_requests(self):  
        yield Request(r"https://github.com/login",  
                      meta={'cookiejar': 1}, 
                      callback=self.post_login)
        
class GithubGoogle(scrapy.Spider):
    name = "githubgoogle"
    def start_requests(self):
        yield Request(r"https://github.com/google")
        
    def parse(self, response):
        projects = response.xpath('//div[@class="d-inline-block mb-1"]/h3/a/text()').extract()
        for p in projects:
            yield {'project': p.strip()}
        next_page = response.xpath('//a[@class="class"]/@href]').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)
                        
class Iqianbang(scrapy.Spider):
    name = "iqianbang"
    def start_requests(self):
        yield Request(r"http:")

        

