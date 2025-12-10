from django.contrib import admin
from .models import (
    Businesses, Locations, Licenses, 
    Suppliers, Pests, BusinessTypes, PlantTypes, SellingSeasons, ShippingRegions,
    Inspections, InspectionFindings, ComplianceAgreements
)

# ==========================================
# INLINES (To see children inside parents)
# ==========================================

class LicenseInline(admin.TabularInline):
    model = Licenses
    extra = 0

class LocationInline(admin.StackedInline):
    model = Locations
    extra = 0
    show_change_link = True

class InspectionFindingInline(admin.TabularInline):
    model = InspectionFindings
    extra = 0

# ==========================================
# ADMIN CONFIGURATIONS
# ==========================================

@admin.register(Businesses)
class BusinessesAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'entity_type', 'mo_city', 'main_contact_name')
    search_fields = ('business_name', 'main_contact_name')
    list_filter = ('entity_type', 'mo_state')
    
    # This replaces the old "BusinessSuppliersInline" and similar errors.
    # Django will now show these as nice search boxes on the Business page.
    filter_horizontal = ('suppliers', 'business_types', 'plant_types', 'selling_seasons', 'shipping_regions')
    
    inlines = [LocationInline]

@admin.register(Locations)
class LocationsAdmin(admin.ModelAdmin):
    list_display = ('business', 'city', 'address', 'store_number')
    search_fields = ('business__business_name', 'address', 'city')
    # This allows you to add Licenses directly inside the Location page
    inlines = [LicenseInline]

@admin.register(Inspections)
class InspectionsAdmin(admin.ModelAdmin):
    list_display = ('location', 'inspection_date', 'passes_inspection', 'inspected_by')
    list_filter = ('passes_inspection', 'inspection_date')
    inlines = [InspectionFindingInline]

# ==========================================
# REGISTER LOOKUP TABLES
# ==========================================
# We register these so you can edit the drop-down lists
admin.site.register(Licenses)
admin.site.register(Suppliers)
admin.site.register(Pests)
admin.site.register(BusinessTypes)
admin.site.register(PlantTypes)
admin.site.register(SellingSeasons)
admin.site.register(ShippingRegions)
admin.site.register(ComplianceAgreements)
