"""
Unit tests for the pages app.
"""
from pathlib import Path

import lxml.html
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.pages.models import Page, PageLink
from apps.pages.tasks import crawl_data, parse_data


class PageTests(APITestCase):
    """
    Test page tasks and endpoints.
    """

    page_1 = {
        "id": 1,
        "url": "https://www.lipsum.com/",
    }

    page_2 = {
        "id": 2,
        "url": "https://www.yahoo.com/",
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
        self.assertEqual(page_updated.stats["total_links"], page_links)

    def test_delete_success(self):
        """
        Test delete page.
        """
        # save page to db
        page = Page(url=self.page_1["url"], stats={"total_links": 0, "unique_links": 0})
        page.save()

        # check page exists
        page_exists = Page.objects.filter(id=page.id).exists()
        self.assertTrue(page_exists)

        # delete page
        page_delete = reverse("page-update-delete", kwargs={"page_id": page.id})
        response = self.client.delete(page_delete, format="json")

        self.assertTrue(response.status_code, 204)

    def test_update_success(self):
        """
        Test update page.
        """
        # save page to db
        page = Page(url=self.page_1["url"], stats={"total_links": 0, "unique_links": 0})
        page.save()

        # check page exists
        page_exists = Page.objects.filter(id=page.id).exists()
        self.assertTrue(page_exists)

        payload = {
            "url": "https://www.theverge.com/",
        }

        # update page
        page_delete = reverse("page-update-delete", kwargs={"page_id": page.id})
        response = self.client.put(page_delete, payload, format="json")

        self.assertTrue(response.status_code, 200)
        self.assertEqual(response.data["url"], payload["url"])

    def test_list_pages_success(self):
        """
        Test list pages.
        """
        # save page to db
        page_1 = Page(
            url=self.page_1["url"], stats={"total_links": 0, "unique_links": 0}
        )
        page_1.save()

        page_2 = Page(
            url=self.page_2["url"], stats={"total_links": 0, "unique_links": 0}
        )
        page_2.save()

        # check page exists
        page_exists_1 = Page.objects.filter(id=page_1.id).exists()
        self.assertTrue(page_exists_1)
        page_exists_2 = Page.objects.filter(id=page_2.id).exists()
        self.assertTrue(page_exists_2)

        # list pages
        page_list = reverse("pages-list")
        response = self.client.get(page_list, format="json")
        res_json = response.json()

        self.assertTrue(response.status_code, 200)
        self.assertEqual(len(res_json), 2)
        self.assertEqual(res_json[0]["url"], self.page_1["url"])
        self.assertEqual(res_json[1]["url"], self.page_2["url"])
