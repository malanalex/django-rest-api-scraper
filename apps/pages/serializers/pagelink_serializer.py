"""
Page serializer.
"""
from rest_framework import serializers

from apps.pages.models import PageLink


class PageLinkSerializer(serializers.ModelSerializer):
    """
    Page link serializer.
    """

    class Meta:
        """
        Meta class.
        """

        model = PageLink
        fields = "__all__"
