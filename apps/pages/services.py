"""
Page service module.
"""
import time

from rest_framework.exceptions import ValidationError

from apps.pages.tasks import crawl_data, parse_data

from .models import Page, PageLink


def download_job(url: str) -> str or bool:
    """
    Download html data.

    :param str url: Url to be scraped
    """
    try:
        run_download = crawl_data.apply_async(args=[url])
        while not run_download.ready():
            time.sleep(1)

        # verify download job status
        if (
            run_download.successful()
            and isinstance(run_download.info, list)
            and not str(run_download.info[1]).startswith(("4", "5"))
        ):
            page = Page(url=url, stats={"total_links": 0, "unique_links": 0})
            page.save()

            if page:
                return (run_download.info[0], page.id)
        return False
    except Exception:
        raise ValidationError("Download job failed. Please try again.")


def parse_job(html_str: str, page_id: int) -> bool:
    """
    Parse html data.

    :param str html_str: Scraped data payload
    :param int page_id: scraped page pk
    """
    try:
        parsing_job = parse_data.apply_async(args=[html_str, page_id])
        while not parsing_job.ready():
            time.sleep(1)

        # verify parsing job status
        if parsing_job.successful() and isinstance(parsing_job.info, int):
            page_check = PageLink.objects.filter(page_id=page_id).count()
            if page_check and page_check == parsing_job.info:
                return True
            return False
    except Exception:
        raise ValidationError("Parsing job failed. Please try again.")
