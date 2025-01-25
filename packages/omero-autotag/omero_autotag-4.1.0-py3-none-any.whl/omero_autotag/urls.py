from django.urls import re_path
from . import views

urlpatterns = [
    re_path(
        r"^get_image_detail_and_tags/$",
        views.get_image_detail_and_tags,
        name="webtagging_get_image_detail_and_tags",
    ),
    # process main form submission
    re_path(
        r"^auto_tag/processUpdate/$",
        views.process_update,
        name="webtagging_process_update",
    ),
    # Create tags for tags dialog
    re_path(r"^create_tag/$", views.create_tag, name="webtagging_create_tag"),
]
