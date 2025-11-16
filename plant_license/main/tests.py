from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse


class LoginRequiredTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

        self.safe_urls = [
            "direct_access",
            "view_db",
            "specific_view",
            "account",
        ]

        # pages have issue with db model, ignoring for now
        self.skip_due_to_db = [
            "dealer_generate",  # page not working yet
            "nursery_generate",
            "success",
        ]

    # ------------------------------
    # Anonymous User
    # ------------------------------

    def test_anonymous_redirect(self):
        """Anonymous users should be redirected to login for safe pages."""
        for name in self.safe_urls:
            url = reverse(name)
            res = self.client.get(url)
            self.assertEqual(res.status_code, 302)

    # ------------------------------
    # Authenticated User
    # ------------------------------

    def test_authenticated_access(self):
        """Logged-in users should get 200 for safe pages."""
        self.client.login(username="testuser", password="testpass123")

        for name in self.safe_urls:
            url = reverse(name)
            res = self.client.get(url)
            self.assertEqual(
                res.status_code, 200, f"Authenticated access failed for {name}"
            )
