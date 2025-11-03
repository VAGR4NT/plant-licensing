from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Root redirect → /login/
    path("", RedirectView.as_view(pattern_name="login", permanent=False)),
    # Login/logout
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="main/login/index.html",
            redirect_authenticated_user=True,  # ✅ key addition
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    # Protected routes
    path("direct-access/", views.direct_access_view, name="direct_access"),
    path("view/", views.view_db_view, name="view_db"),
    path("generate-forms/", views.generate_forms_view, name="generate_forms"),
    path("update/", views.update_view, name="update"),
    path("update/<int:pk>/", views.update_view, name="update_pk"),
    path("success/", views.update_success, name="success"),
    path('update/<str:model>/<int:pk>/', views.update_view, name='update'),
    path("user-info/", views.user_info_view, name="user_info"),
    path("specific_view/", views.specific_view, name="specific_view"), 
    path("account/", views.account_view, name="account"),
]
