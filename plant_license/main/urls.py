from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from . import views
from .views import download_nursery_pdf
from .views import export_table_as_csv
from .views import export_table_as_xlsx
from .views import download_template_version
from .views import activate_template_version
from .views import remove_template


from django.contrib import admin
from .autocomplete import SupplierAutocomplete

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
    path("admin/", admin.site.urls),
    # Protected routes
    path("direct-access/", views.direct_access_view, name="direct_access"),
    path("view/", views.view_db_view, name="view_db"),
    path("generate-forms/", views.nursery_generate, name="generate_forms"),
    path("update/<int:ct>/<int:pk>/", views.update_view, name="update"),
    path("add_business/", views.add_business.as_view(), name="add_business"),
    path(
        "add_location/<int:parent_id>/",
        views.add_location.as_view(),
        name="add_location",
    ),
    path(
        "add_compliance_agreements/<int:parent_id>/",
        views.add_compliance_agreement.as_view(),
        name="add_compliance_agreement",
    ),
    path("add_supplier/", views.add_supplier.as_view(), name="add_supplier"),
    path(
        "supplier-autocomplete/",
        SupplierAutocomplete.as_view(),
        name="supplier-autocomplete",
    ),
    path("user-info/", views.user_info_view, name="user_info"),
    path("specific_view/", views.specific_view, name="specific_view"),
    path("independent_view/<int:ct>/", views.independent_view, name="independent_view"),
    path("account/", views.account_view, name="account"),
    # nursery and dealer pdf/eml generation
    path("nursery_generate/", views.nursery_generate, name="nursery_generate"),
    path("dealer_generate/", views.dealer_generate, name="dealer_generate"),
    path("pdf_update/", views.pdf_update, name="pdf_update"),
    path(
        "templates/download/<int:template_id>/",
        views.download_template_version,
        name="download_template",
    ),
    path(
        "templates/remove/<int:template_id>/",
        views.remove_template,
        name="remove_template",
    ),
    path(
        "templates/activate/<int:template_id>/",
        views.activate_template_version,
        name="activate_template",
    ),
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
    path("export_table_csv/", export_table_as_csv, name="export_table_csv"),
    path("export_table_xlsx/", export_table_as_xlsx, name="export_table_xlsx"),
]
