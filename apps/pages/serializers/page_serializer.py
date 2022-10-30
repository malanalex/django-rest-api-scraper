"""
Page serializer.
"""
from rest_framework import serializers

from apps.pages.models import Page

from .pagelink_serializer import PageLinkSerializer


class PageSerializer(serializers.ModelSerializer):
    """
    Page serializer.
    """

    links = PageLinkSerializer(many=True, read_only=True)

    class Meta:
        """
        Meta class.
        """

        model = Page
        fields = ("id", "url", "stats", "added_at", "processed_at", "links")
        write_only_fields = ("url",)
        read_only_fields = (
            "id",
            "processed_at",
            "added_at",
            "stats",
            "links",
        )

    def check_duplicate_url(self, url):
        """
        Check if url already exists.
        """
        return Page.objects.filter(url=url).first()
