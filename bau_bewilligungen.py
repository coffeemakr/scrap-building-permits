import scrapy



class Bauamt(object):
    def __init__(self, name, title_announcement, url):
        self.name = name
        self.title_announcement = title_announcement
        self.url = url

    def parse(response):
        result = {}
        for parent in response.css('.element .list'):
            if parent.css('h3').xpath('text()').extract_first() == self.title_announcement:
                result['announcements'] = list(parse_announcement_list(response, parent))
        return result

    def parse_announcement_list(response, list_content):
        elements = list_content.css('li a')
        for element in elements:
            yield {
                'institution': self.name,
                'date': element.css('.date').xpath('text()').extract_first(),
                'title': element.css('.title').xpath('text()').extract_first(),
                'url': response.urljoin(element.xpath('@href').extract_first())
            }



hochbau = Bauamt(
    name="Hochbau",
    title_announcement="Bauausschreibungen",
    url = 'https://www.buelach.ch/themen/wohnen_bauen/tiefbau/'
)

tiefbau = Bauamt(
    name="Tiefbau",
    title_announcement="Ausschreibungen Tiefbau",
    url = 'https://www.buelach.ch/themen/wohnen_bauen/tiefbau/'
)


class BauamtSpider(scrapy.Spider):

    title_announcement = "Ausschreibungen Tiefbau"

    def 

    def parse(self, response):

