from django.contrib import admin
from . import models

# -----------------------------------------------------------------
#  STEP 1: Define INLINES for "child" objects.
#  This is the magic that solves your "hunting" problem.
#  It puts related models directly onto the parent's edit page.
# -----------------------------------------------------------------

class LicenseInline(admin.TabularInline):
    """
    Shows a table of Licenses directly on the Location edit page.
    """
    model = models.Licenses
    extra = 0  # Don't show new blank forms by default


class LocationInline(admin.TabularInline):
    """
    Shows a table of Locations directly on the Business edit page.
    """
    model = models.Locations
    extra = 0
    show_change_link = True # Adds a link to edit the full location


class ComplianceAgreementInline(admin.TabularInline):
    """
    Shows Compliance Agreements on the Business edit page.
    """
    model = models.ComplianceAgreements
    extra = 0


# -----------------------------------------------------------------
#  STEP 2: Define INLINES for your M2M "through" tables.
#  This is how you manage those complex relationships.
# -----------------------------------------------------------------

class BusinessSuppliersInline(admin.TabularInline):
    """
    Lets you add/remove Suppliers from a Business.
    'autocomplete_fields' makes finding a supplier easy.
    """
    model = models.BusinessSuppliers
    extra = 0
    autocomplete_fields = ['supplier']


class BusinessPlantTypesInline(admin.TabularInline):
    model = models.BusinessPlantTypes
    extra = 0
    autocomplete_fields = ['plant_type']


class BusinessSellingSeasonsInline(admin.TabularInline):
    model = models.BusinessSellingSeasons
    extra = 0
    autocomplete_fields = ['season']


class BusinessShippingRegionsInline(admin.TabularInline):
    model = models.BusinessShippingRegions
    extra = 0
    autocomplete_fields = ['region']


class BusinessTypeMapInline(admin.TabularInline):
    model = models.BusinessTypeMap
    extra = 0
    autocomplete_fields = ['type']


# -----------------------------------------------------------------
#  STEP 3: Create the "Hub" Admin Views
#  This is where we bring all the inlines together.
# -----------------------------------------------------------------

@admin.register(models.Businesses)
class BusinessAdmin(admin.ModelAdmin):
    """
    This is now your main "dashboard" for a Business.
    """
    list_display = (
        'business_name', 
        'main_contact_name', 
        'main_contact_phone', 
        'mo_city', 
        'mo_state',
        'is_deleted',
    )
    list_filter = ('mo_state', 'is_deleted', 'entity_type')
    search_fields = (
        'business_name', 
        'dba_business_name', 
        'main_contact_name', 
        'main_contact_email',
    )
    
    # Organize the main edit page
    fieldsets = (
        ('Business Info', {
            'fields': (
                'business_name', 
                'dba_business_name', 
                'entity_type', 
                'class_field', 
                'acreage'
            )
        }),
        ('Main Contact', {
            'fields': ('main_contact_name', 'main_contact_phone', 'main_contact_email')
        }),
        ('Mailing Address', {
            'fields': ('mo_address', 'mo_city', 'mo_state', 'mo_zip')
        }),
        ('Renewal/Labels', {
            'fields': (
                'wants_email_renewal', 
                'wants_email_license', 
                'wants_labels', 
                'num_labels'
            )
        }),
        ('Deletion Info', {
            'classes': ('collapse',), # Hide this section by default
            'fields': ('is_deleted', 'date_deleted', 'deletion_reason')
        }),
    )

    # This is the solution: Show all related data on one page.
    inlines = [
        LocationInline,
        ComplianceAgreementInline,
        BusinessSuppliersInline,
        BusinessPlantTypesInline,
        BusinessSellingSeasonsInline,
        BusinessShippingRegionsInline,
        BusinessTypeMapInline,
    ]


@admin.register(models.Locations)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'address', 
        'city', 
        'state', 
        'zip_code', 
        'business', 
        'county'
    )
    list_filter = ('state', 'county')
    search_fields = (
        'address', 
        'city', 
        'zip_code', 
        'store_number', 
        'business__business_name' # Allows searching by the business name!
    )
    
    # Makes picking the Business easy (no giant dropdown)
    autocomplete_fields = ['business']

    # Show related licenses on this location's page
    inlines = [LicenseInline]


@admin.register(models.Suppliers)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('supplier_name', 'city', 'state', 'zip_code')
    
    # This search_fields is REQUIRED for 'autocomplete_fields'
    # in BusinessSuppliersInline to work.
    search_fields = ['supplier_name']


# -----------------------------------------------------------------
#  STEP 4: Register the "Lookup" tables
#  We just need to make them searchable for the inlines.
# -----------------------------------------------------------------

@admin.register(models.PlantTypes)
class PlantTypesAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(models.SellingSeasons)
class SellingSeasonsAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(models.ShippingRegions)
class ShippingRegionsAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(models.BusinessTypes)
class BusinessTypesAdmin(admin.ModelAdmin):
    search_fields = ['type_name']


@admin.register(models.Pests)
class PestsAdmin(admin.ModelAdmin):
    search_fields = ['pest_name']


# -----------------------------------------------------------------
#  STEP 5: Register the "child" models (optional but good)
#  This lets you see a global list of *all* licenses, etc.
# -----------------------------------------------------------------

@admin.register(models.Licenses)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ('license_number', 'license_year', 'location')
    list_filter = ('license_year',)
    autocomplete_fields = ['location']


@admin.register(models.ComplianceAgreements)
class ComplianceAgreementAdmin(admin.ModelAdmin):
    list_display = ('agreement_number', 'business')
    autocomplete_fields = ['business']
