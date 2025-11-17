from dal import autocomplete
from .models import Suppliers

class SupplierAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Suppliers.objects.none()

        qs = Suppliers.objects.all()

        if self.q: 
            qs = qs.filter(supplier_name__icontains=self.q)

        return qs
