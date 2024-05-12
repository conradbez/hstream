from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("run_hs", views.run_hs, name="run_hs"),
    path(
        "partial_or_full_html_content",
        views.partial_or_full_html_content,
        name="partial_or_full_html_content",
    ),
    path(
        "set_component_value",
        views.set_component_value,
        name="set_component_value",
    ),
]
