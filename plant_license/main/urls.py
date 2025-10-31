from django.urls import path
from . import views
from .views import download_nursery_pdf

urlpatterns = [
    path("", views.home_view, name="home"),
    path("direct-access/", views.direct_access_view, name="direct_access"),
    path("view/", views.view_db_view, name="view_db"),
    path("generate-forms/", views.generate_forms_view, name="generate_forms"),
    path("update/", views.update_view, name="update"),
    path("user-info/", views.user_info_view, name="user_info"),
    path("specific_view/<str:category>/", views.specific_view, name="specific_view"),
    path("nursery_generate/", views.nursery_generate, name="nursery_generate"),
    path("dealer_generate/", views.dealer_generate, name="dealer_generate"),
    path("nursery/<int:business_id>/download/", download_nursery_pdf, name="download_nursery_pdf"),
]
