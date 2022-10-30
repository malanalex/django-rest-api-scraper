"""
Pages url configuration.
"""
from django.urls import path

from .views import PageCreateView, PagesListView, PageUpdateDeleteView

urlpatterns = [
    path("list/", view=PagesListView.as_view(), name="pages-list"),
    path("create/", view=PageCreateView.as_view(), name="page-create"),
    path(
        "<int:page_id>/",
        view=PageUpdateDeleteView.as_view(),
        name="page-update-delete",
    ),
]
