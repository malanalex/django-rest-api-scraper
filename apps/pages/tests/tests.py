"""
Unit tests for the pages app.
"""
from pathlib import Path

import lxml.html
from rest_framework.test import APITestCase

from apps.pages.models import Page, PageLink
from apps.pages.tasks import crawl_data, parse_data


class PageServiceTests(APITestCase):
    """
    Test services
    """

    page_1 = {
        "id": 1,
        "url": "https://www.lipsum.com/",
    }

    common_tags = ["html", "body", "p", "div"]

    def setUp(self):
        pass

    def tearDown(self):
        self.client.logout()

    def test_crawl_data_success(self):
        """
        Page crawl task success.
        """
        response = crawl_data(self.page_1["url"])

        self.assertEqual(response[1], 200)

        for tag in self.common_tags:
            self.assertTrue(tag in response[0])

    def test_parse_data_success(self):
        """
        Page parse task success.
        """
        path = Path(__file__).parent / "test_data/html_test.txt"

        # save page to db
        page = Page(url=self.page_1["url"], stats={"total_links": 0, "unique_links": 0})
        page.save()

        with open(path) as f:
            html_data = f.read()
            f.close()

        # check the number of links in the html
        tree = lxml.html.fromstring(html_data)
        tag_parse = tree.xpath("//a")
        links_found = len(tag_parse)

        # pase html data
        response = parse_data(html_data, page.id)

        # compare the number of links found
        self.assertEqual(response, links_found)

        page_links = PageLink.objects.count()
        self.assertEqual(response, page_links)

        page_updated = Page.objects.filter(id=page.id).first()
        self.assertEqual(page_updated.stats['total_links'], page_links)