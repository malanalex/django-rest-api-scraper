"""
Page serializer.
"""
from rest_framework import serializers

from .models import Page, PageLink


class PageSerializer(serializers.ModelSerializer):
    """
    Page serializer.
    """

    # list of all links related to this page
    links = serializers.SerializerMethodField()

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

    def get_links(self, obj):
        """
        Get all links related to this page.
        """
        return PageLink.objects.filter(page=obj).values(
            "id", "href", "rel", "title", "added_at"
        )
