"""
Pages views.
"""
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Page
from .serializers import PageSerializer
from .services import download_job, parse_job


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
        # validate payload
        if not request.data:
            raise ValidationError("Invalid input. No data provided.")
        if not isinstance(request.data["url"], str) or "url" not in request.data.keys():
            raise ValidationError("Invalid input. Please provide a string url.")

        # validate duplicate url
        page_status = Page.objects.filter(url=request.data["url"]).first()
        if page_status:
            return Response(
                {"message": "Page already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # run download job
        download_job_run = download_job(request.data["url"])
        if download_job_run:
            # run parse job
            parse_job_status = parse_job(download_job_run[0], download_job_run[1])
            if parse_job_status:
                return Response(
                    {"message": "Page successfully created and parsed."},
                    status=status.HTTP_201_CREATED,
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
