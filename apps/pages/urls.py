"""
Pages url configuration.
"""
from django.urls import path

from . import views

urlpatterns = [
    path("list/", view=views.PagesListView.as_view(), name="pages-list"),
    path("create/", view=views.PageCreateView.as_view(), name="page-create"),
    path(
        "<int:page_id>/",
        view=views.PageUpdateDeleteView.as_view(),
        name="page-update-delete",
    ),
]
