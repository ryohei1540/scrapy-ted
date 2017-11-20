# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy import Request

from scrapy.selector import Selector

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

from time import sleep

from ted.spiders import Script
from ted.items import TedItem


class JobsSpider(Spider):
    name = 'jobs'
    allowed_domains = ['ted.com']
    start_urls = ['https://www.ted.com/talks/']

    def parse(self, response):
        jobs = response.xpath(
            "//div[@class='row row-sm-4up row-lg-6up row-skinny']/div[contains(@class, 'col')]")
        for job in jobs:
            script = Script()
            script.set_initial(response, job)
            yield Request(script._url, callback=self.parse_details, meta={'Script': script})
        next_page_url = response.xpath(
            "//a[@class='pagination__next pagination__flipper pagination__link']/@href").extract_first()
        absolute_next_page_url = response.urljoin(next_page_url)
        yield Request(absolute_next_page_url)

    def parse_details(self, response):
        script = response.meta.get('Script')
        headless = self.select_headless(response.url)
        try:
            headless = self.open_tags()
        except NoSuchElementException:
            self.logger.info("Don't find tags.")
        absolute_url = response.url.replace('details', 'transcript')
        script.set_detail(headless)
        self.driver.quit()
        yield Request(absolute_url, callback=self.parse_transcript, meta={'Script': script})

    def parse_transcript(self, response):
        script = response.meta.get('Script')
        headless = self.select_headless(response.url)
        script.set_transcript(headless)
        self.driver.quit()
        item = TedItem()
        item['title'] = script._title
        item['published_date'] = script._published_date
        item['time'] = script._time
        item['views'] = script._views
        item['tags'] = script._tags
        item['person'] = script._person
        item['content'] = script._content
        item['url'] = script._url
        yield item

    def select_headless(self, absolute_url):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.get(absolute_url)
        sleep(1)
        headless = Selector(text=self.driver.page_source)
        return headless

    def open_tags(self):
        try:
            tags = self.driver.find_element_by_xpath(
              "//button[@class=' sb c:gray f:2 l-s:t p-r:1 ']")
            self.driver.execute_script("arguments[0].click();", tags)
            headless = Selector(text=self.driver.page_source)
            return headless
        except NoSuchElementException as e:
            raise NoSuchElementException("Don't find tags") from e
