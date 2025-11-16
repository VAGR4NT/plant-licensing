from dal import autocomplete
from .models import Suppliers

class SupplierAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Only allow logged-in users to access this
        if not self.request.user.is_authenticated:
            return Suppliers.objects.none()

        qs = Suppliers.objects.all()

        if self.q: # 'self.q' is the user's search query
            qs = qs.filter(supplier_name__icontains=self.q)

        return qs
