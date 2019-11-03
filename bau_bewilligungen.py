import lxml

import datetime
import json
import re
import requests_cache
import requests_html
import urllib.parse
import bleach
from dominate import document, tags
import xml.etree.cElementTree as ET
from email import utils
from bs4 import BeautifulSoup

requests_cache.install_cache('scrap_cache')

ALLOWED_TAGS = [
    "h1", "h2", "h3", "h4", "h5", "h6",
    "b", "i", "strong", "em", "tt",
    "p", "br",
    "span", "div", "blockquote", "code", "hr",
    "ul", "ol", "li", "dd", "dt",
    "pre"
]


def default_json(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()


class Bauamt(object):
    def __init__(self, name, title_announcement, url):
        self.name = name
        self.title_announcement = title_announcement
        self.url = url


class Parser(object):
    def __init__(self, session):
        self.session = session

    def parse(self, bauamt):
        response = self.session.get(bauamt.url)
        base_url = response.html.base_url
        for parent in response.html.find('.element .list'):
            title = parent.find('h3', first=True)
            if title.text == bauamt.title_announcement:
                for announcement in self.parse_announcement_list(base_url, parent):
                    announcement['institution'] = bauamt.name
                    announcement['city'] = 'Bülach'
                    yield announcement
                return

    def parse_announcement_list(self, base_url, list_content):
        elements = list_content.find('li a')
        for element in elements:
            url = urllib.parse.urljoin(base_url, element.attrs['href'])
            id = re.match(r'.*-([0-9]+)/$', url)
            if id is None:
                raise ValueError(f"Unable to find id: {url}")
            id = id.group(1)
            result = {
                'date': datetime.datetime.strptime(element.find('.date', first=True).text, "%d.%m.%Y"),
                'url': url,
                'id': id
            }
            result.update(self.parse_announcemnet_content(url))
            yield result

    def parse_announcemnet_content(self, url):
        response = self.session.get(url)
        html = response.html
        content = html.find('div#main', first=True)
        content.url = html.base_url

        print(content.base_url)
        documents = content.find('ul', first=True)
        if documents is not None:
            documents = list(documents.absolute_links)
        body = bleach.clean(content.raw_html.decode('utf-8'), tags=ALLOWED_TAGS, strip=True)
        #body = BeautifulSoup(body, "lxml")
        #body = body.prettify()
        return {
            "content": body,
            "title": content.find('h1', first=True).text,
            "documents": documents,
        }


hochbau = Bauamt(
    name="Hochbau",
    title_announcement="Bauausschreibungen",
    url='https://www.buelach.ch/themen/wohnen_bauen/hochbau/'
)

tiefbau = Bauamt(
    name="Tiefbau",
    title_announcement="Ausschreibungen Tiefbau",
    url='https://www.buelach.ch/themen/wohnen_bauen/tiefbau/'
)


def spider():
    result = []
    session = requests_html.HTMLSession()
    parser = Parser(session)
    for bauamt in [hochbau]:
        result += list(parser.parse(bauamt))
    print(json.dumps(result, indent=4, default=default_json))
    root = ET.Element("rss", version='2.0')
    channel = ET.SubElement(root, "channel")
    ET.SubElement(channel, "title").text = "Test"
    ET.SubElement(channel, "description").text = "Test"
    ET.SubElement(channel, "link").text = "http://localhost:8080/rss"


    for item in result:
        itemTag = ET.SubElement(channel, "item")
        ET.SubElement(itemTag, "title").text = item['title']
        ET.SubElement(itemTag, "description").text = item['content']
        ET.SubElement(itemTag, "link").text = item['url']
        ET.SubElement(itemTag, "guid", isPermaLink="false").text = item['url']
        ET.SubElement(itemTag, 'pubDate').text = utils.format_datetime(item['date'])
    tree = ET.ElementTree(root)
    tree.write("test.xml",
               encoding='utf-8',
               xml_declaration=True
               )

if __name__ == '__main__':
    spider()
