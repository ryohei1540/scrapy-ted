import re
import itertools


class Script:

    def __init__(self):
        self._person = []
        self._title = ""
        self._published_date = ""
        self._time = ""
        self._views = ""
        self._tags = []
        self._content = ""
        self._url = ""

    def set_initial(self, response, job):
        relative_url = job.xpath(
            "div[@class='m3']/div[@class='talk-link']/div[@class='media media--sm-v']/div[@class='media__image media__image--thumb talk-link__image']/a/@href").extract_first() + "/details"
        self._url = response.urljoin(relative_url)
        self._title = job.xpath(
            "div[@class='m3']/div[@class='talk-link']/div[@class='media media--sm-v']/div[@class='media__message']/h4[@class='h9 m5']/a/text()").extract_first().strip()
        self._published_date = job.xpath(
            "div[@class='m3']/div[@class='talk-link']/div[@class='media media--sm-v']/div[@class='media__message']/div[@class='meta']/span[@class='meta__item']/span[@class='meta__val']/text()").extract_first().strip()
        self._time = job.xpath("div[@class='m3']/div[@class='talk-link']/div[@class='media media--sm-v']/div[@class='media__image media__image--thumb talk-link__image']/a[@class=' ga-link']/span[@class='thumb thumb--video thumb--crop-top']/span[@class='thumb__duration']/text()").extract_first()

    def set_detail(self, headless):
        name_list = []
        occupation_list = []
        self._views = headless.xpath(
            "//span[@class=' f-w:700 f:3 ']/text()").extract_first().replace(",", "")
        names = headless.xpath("//div[@class='m-b:.2']")
        for name in names:
            name_list.append(name.xpath("a/text()").extract_first().strip())
        occupations = headless.xpath("//div[@class='m-b:.2']/span[1]/span[2]")
        if occupations != "":
            for occupation in occupations:
                target = occupation.xpath("text()").extract_first().lower()
                splitted_target = re.split(', | and ', target)
                occupation_list.append(splitted_target)
        self.set_person(name_list, occupation_list)
        tags = headless.xpath(
            "//div[@class='Grid__cell w:1of4@md d:n d:i-b@md']/div/ul/li")
        for tag in tags:
            self._tags.append(tag.xpath("a/text()").extract_first().lower())

    def set_person(self, name_list, occupation_list):
        data = {}
        for name, occupation in itertools.zip_longest(name_list, occupation_list):
            data["name"] = name
            data["occupation"] = occupation
            self._person.append(data.copy())

    def set_transcript(self, headless):
        contents_list = []
        total_contents = headless.xpath(
            "//div[@class=' Grid Grid--with-gutter d:f@md p-b:4 ']")
        for total_content in total_contents:
            jobs = total_content.xpath("div/p/span")
            for job in jobs:
                contents_list.append(
                    job.xpath("a/text()").extract_first().replace("\n", " "))
        self._content = " ".join(contents_list)
