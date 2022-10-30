"""
Celery tasks module.
"""
from __future__ import absolute_import, unicode_literals

import random
import string
from typing import Union

import lxml.html
import requests
from celery import chain
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone
from requests.adapters import HTTPAdapter, Retry
from rest_framework.exceptions import ValidationError

from apps.pages.models import Page, PageLink
from apps.pages.tasks.task_base import LogErrorsTask
from common.headers import headers_list
from core.celery import app

from .task_base import LogErrorsTask


@app.task
def scraping_job(url: str):
    """
    Download and extract data from url.

    :param str url: Url to be scraped
    """
    ch = chain(
        crawl_data.s(url).set(queue="download_queue"),
        parse_data.s().set(queue="parse_queue"),
    ).apply_async(countdown=0.1)

    return ch


@app.task(
    base=LogErrorsTask,
    queue="download_queue",
    autoretry_for=(Exception,),
    max_retry=2,
    default_retry_delay=3,
)
def crawl_data(url: str) -> Union[str, int]:
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

        if response.status_code == 200:
            # save page instance
            page = Page(url=url, stats={"total_links": 0, "unique_links": 0})
            page.save()

            # save file contents
            file_name = "".join(
                random.choices(
                    (string.ascii_lowercase + string.ascii_uppercase + string.digits),
                    k=10,
                )
            )
            path = default_storage.save(
                f"download_data/{file_name}.txt", ContentFile(response.text)
            )

            if isinstance(path, str) and isinstance(page.id, int):
                return path, page.id
            raise
        raise
    except Exception as e:
        raise ValidationError(f"Something went wrong with the scraper : {str(e)}")


@app.task(
    base=LogErrorsTask,
    queue="parse_queue",
    autoretry_for=(Exception,),
    max_retry=2,
    default_retry_delay=2,
)
def parse_data(data: Union[str, int]) -> int:
    """
    Parse html data.

    :param str html_str: Scraped data payload
    :param int page_id: scraped page pk
    """
    try:
        path, page_id = data
        links = []
        if default_storage.exists(path):
            html_str = default_storage.open(path).read()

            # parse html
            tree = lxml.html.fromstring(html_str)
            tag_parse = tree.xpath("//a")

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
            default_storage.delete(path)
            return len(total_insertions)
        return 0
    except Exception as e:
        raise ValidationError(f"Something went wrong with the parser : {str(e)}")
