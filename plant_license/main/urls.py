from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Root redirect → /login/
    path("", RedirectView.as_view(pattern_name="login", permanent=False)),
    # Login / Logout
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="main/login/index.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    # Protected routes
    path("direct-access/", views.direct_access_view, name="direct_access"),
    path("view/", views.view_db_view, name="view_db"),
    path("generate-forms/", views.nursery_generate, name="generate_forms"),
    path("update/<int:ct>/<int:pk>/", views.update_view, name="update"),
    path("add_business/", views.add_business, name="add_business"),
    path("user-info/", views.user_info_view, name="user_info"),
    path("specific_view/", views.specific_view, name="specific_view"),
    path("account/", views.account_view, name="account"),
    # Nursery + Dealer listing pages
    path("nursery_generate/", views.nursery_generate, name="nursery_generate"),
    path("dealer_generate/", views.dealer_generate, name="dealer_generate"),
    # Nursery PDF actions
    path(
        "nursery/<int:business_id>/pdf/",
        views.download_nursery_pdf,
        name="download_nursery_pdf",
    ),
    path(
        "nursery/<int:business_id>/preview/",
        views.preview_nursery_pdf,
        name="nursery_preview",
    ),
    path(
        "nursery/<int:business_id>/eml/",
        views.download_nursery_eml,
        name="download_nursery_eml",
    ),
    # Dealer PDF
    path(
        "dealer/<int:business_id>/pdf/",
        views.download_dealer_pdf,
        name="download_dealer_pdf",
    ),
]
