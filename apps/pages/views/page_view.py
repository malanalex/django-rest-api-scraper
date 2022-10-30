"""
Pages views.
"""
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.pages.models import Page
from apps.pages.serializers import PageSerializer
from apps.pages.tasks import scraping_job


class PagesListView(generics.ListAPIView):
    """
    List all pages.
    """

    queryset = Page.objects.all()
    model = Page
    serializer_class = PageSerializer


class PageCreateView(generics.CreateAPIView):
    """
    Create pages.
    """

    queryset = Page.objects.all()
    model = Page
    serializer_class = PageSerializer

    def post(self, request, *args, **kwargs):
        """
        Create page.
        """
        payload_valid = PageSerializer(data=request.data).is_valid()
        page_duplicate = PageSerializer(data=request.data).check_duplicate_url(
            request.data["url"]
        )
        if page_duplicate:
            return Response(
                {"message": "Page already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if payload_valid:
            scraping_job(request.data["url"])
            return Response(
                {"message": "Page successfully submitted."},
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            {"message": "Something went wrong. Please try again."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class PageUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    Update and Delete pages.
    """

    queryset = Page.objects.all()
    model = Page
    serializer_class = PageSerializer

    def get_object(self):
        """
        Retrieve page.

        ```
        :raise: ValidationError if page not found or is invalid
        ```
        """
        try:
            page = Page.objects.get(id=self.kwargs.get("page_id"))
        except:
            raise ValidationError("Page not found")
        return page

    def update(self, request, *args, **kwargs):
        """
        Update page.

        ```
        :return: Empty response with status 200
        ```
        """
        page = self.get_object()
        serializer = self.get_serializer(page, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Delete page.

        ```
        :return: Response with status 204
        ```
        """
        page = self.get_object()
        page.delete()
        return Response(
            {"message": "Page deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )
