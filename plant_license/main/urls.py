from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from . import views
from .views import download_nursery_pdf
from .views import export_table_as_csv
from .views import export_table_as_xlsx

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
    # nursery and dealer pdf/eml generation
    path("nursery_generate/", views.nursery_generate, name="nursery_generate"),
    path("dealer_generate/", views.dealer_generate, name="dealer_generate"),
    path(
        "<str:kind>/<int:business_id>/preview/", views.preview_pdf, name="preview_pdf"
    ),
    path(
        "<str:kind>/<int:business_id>/download/",
        views.download_pdf,
        name="download_pdf",
    ),
    path(
        "<str:kind>/<int:business_id>/email/", views.download_eml, name="download_eml"
    ),
    path('export_table_csv/', export_table_as_csv, name='export_table_csv'),
    path('export_table_xlsx/', export_table_as_xlsx, name='export_table_xlsx'),
]
