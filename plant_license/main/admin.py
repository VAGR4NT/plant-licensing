from django.contrib import admin
from .models import Businesses, Locations, Suppliers

# Register your models here.

admin.site.register(Businesses)
admin.site.register(Locations)
admin.site.register(Suppliers)
