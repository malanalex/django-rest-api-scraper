"""
Celery tasks module.
"""
from __future__ import absolute_import, unicode_literals

import random

import lxml.html
import requests
from django.utils import timezone
from requests.adapters import HTTPAdapter, Retry
from rest_framework.exceptions import ValidationError

from common.headers import headers_list
from core.celery import app

from .models import Page, PageLink


@app.task(queue="download_queue")
def crawl_data(url: str) -> str:
    """
    Scrape html data.

    :param str url: Url to be scraped
    """
    try:
        s = requests.Session()
        retries = Retry(
            total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504]
        )
        s.mount("http://", HTTPAdapter(max_retries=retries))
        response = s.get(url=url, headers=random.choice(headers_list))

        return (response.text, response.status_code)
    except Exception:
        raise ValidationError(
            "Something went wrong with the scraper. Please try again."
        )


@app.task(queue="parse_queue")
def parse_data(html_str: str, page_id: int) -> list:
    """
    Parse html data.

    :param str html_str: Scraped data payload
    :param int page_id: scraped page pk
    """
    try:
        # parse html
        tree = lxml.html.fromstring(html_str)
        tag_parse = tree.xpath("//a")
        links = []

        # get page
        page = Page.objects.filter(id=page_id).first()

        # get all links details
        for link in tag_parse:
            if "href" in link.attrib:
                href = link.get("href")
                rel = link.get("rel") or None
                title = link.get("title") or None
                links.append(PageLink(href=href, rel=rel, title=title, page=page))

        # bulk create page links
        if len(links) > 0:
            total_insertions = PageLink.objects.bulk_create(
                links, ignore_conflicts=True, batch_size=1000
            )

            # update Create Page
            unique_links = len(set([link.href for link in links]))
            Page.objects.filter(id=page_id).update(
                stats={"total_links": len(links), "unique_links": unique_links},
                processed_at=timezone.now(),
            )

            # empty data structure
            links = []
            return len(total_insertions)
        return False
    except Exception:
        raise ValidationError("Something went wrong with parsing. Please try again.")
