from django.shortcuts import redirect
from django.urls import reverse


# this automatically restricts pages unless logged in
class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        login_url = reverse("login")
        logout_url = reverse("logout")

        # Skip if user is authenticated or accessing login/logout/static
        if not request.user.is_authenticated:
            if not (
                request.path.startswith(login_url)
                or request.path.startswith(logout_url)
                or request.path.startswith("/static/")
            ):
                return redirect("login")

        return self.get_response(request)
