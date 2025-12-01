from django.db import models
from django.utils import timezone

# ==========================================
# 1. LOOKUP TABLES (Keeping Plural Names)
# ==========================================

class BusinessTypes(models.Model):
    type_id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'business_types'
        verbose_name = "Business Type"

    def __str__(self):
        return self.type_name


class PlantTypes(models.Model):
    plant_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'plant_types'
        verbose_name = "Plant Type"

    def __str__(self):
        return self.name


class SellingSeasons(models.Model):
    season_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'selling_seasons'
        verbose_name = "Selling Season"

    def __str__(self):
        return self.name


class ShippingRegions(models.Model):
    region_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'shipping_regions'
        verbose_name = "Shipping Region"

    def __str__(self):
        return self.name


class Suppliers(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    supplier_name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'suppliers'
        ordering = ['supplier_name']
        verbose_name_plural = "Suppliers"

    @staticmethod
    def get_add_url():
        return "add_location"

    def __str__(self):
        return self.supplier_name


class Pests(models.Model):
    pest_id = models.AutoField(primary_key=True)
    common_name = models.CharField(max_length=255, unique=True)
    scientific_name = models.CharField(max_length=255, blank=True, null=True)
    pest_type = models.CharField(
        max_length=50, 
        choices=[
            ('Insect', 'Insect'),
            ('Disease', 'Disease'),
            ('Fungus', 'Fungus'),
            ('Mite', 'Mite'),
            ('Weed', 'Weed'),
            ('Other', 'Other')
        ],
        blank=True, null=True
    )

    class Meta:
        db_table = 'pests'
        ordering = ['common_name']
        verbose_name_plural = "Pests"

    def __str__(self):
        return self.common_name


# ==========================================
# 2. CORE ENTITIES (Businesses & Locations)
# ==========================================

class Businesses(models.Model):
    business_id = models.AutoField(primary_key=True)
    
    entity_type = models.CharField(
        max_length=20, 
        choices=[('Dealer', 'Dealer'), ('Nursery', 'Nursery')]
    )
    business_name = models.CharField(max_length=255, unique=True)
    dba_business_name = models.CharField(max_length=255, blank=True, null=True)
    
    # Main Office Address
    mo_address = models.CharField(max_length=255, blank=True, null=True)
    mo_city = models.CharField(max_length=100, blank=True, null=True)
    mo_state = models.CharField(max_length=2, blank=True, null=True)
    mo_zip = models.CharField(max_length=10, blank=True, null=True)
    
    # Contact Info
    main_contact_name = models.CharField(max_length=255, blank=True, null=True)
    main_contact_phone = models.CharField(max_length=30, blank=True, null=True)
    main_contact_email = models.EmailField(max_length=255, blank=True, null=True)
    main_contact_alt_phone = models.CharField(max_length=30, blank=True, null=True)
    main_contact_fax = models.CharField(max_length=30, blank=True, null=True)
    main_contact_alt_email = models.EmailField(max_length=255, blank=True, null=True)

    # Details
    class_code = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B')], db_column='class', blank=True, null=True)
    acreage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    priority_rank = models.CharField(max_length=50, blank=True, null=True)
    
    # Flags
    is_interstate_shipper = models.BooleanField(default=False)
    wants_email_renewal = models.BooleanField(default=False)
    wants_email_license = models.BooleanField(default=False)
    wants_labels = models.BooleanField(default=False)
    num_labels = models.IntegerField(blank=True, null=True)
    
    # System Flags
    is_deleted = models.BooleanField(default=False)
    date_deleted = models.DateField(blank=True, null=True)
    deletion_reason = models.TextField(blank=True, null=True)
    date_applied = models.DateField(default=timezone.now)

    # Legacy / Notes
    formerly_known_as = models.CharField(max_length=255, blank=True, null=True)

    # RELATIONSHIPS
    suppliers = models.ManyToManyField(Suppliers, db_table='business_suppliers', blank=True)
    business_types = models.ManyToManyField(BusinessTypes, db_table='business_type_map', blank=True)
    plant_types = models.ManyToManyField(PlantTypes, db_table='business_plant_types', blank=True)
    selling_seasons = models.ManyToManyField(SellingSeasons, db_table='business_selling_seasons', blank=True)
    shipping_regions = models.ManyToManyField(ShippingRegions, db_table='business_shipping_regions', blank=True)

    class Meta:
        db_table = 'businesses'
        verbose_name_plural = "Businesses"

    def __str__(self):
        return self.business_name


class Locations(models.Model):
    location_id = models.AutoField(primary_key=True)
    business = models.ForeignKey(Businesses, on_delete=models.CASCADE, related_name='locations')
    
    legacy_license_id = models.CharField(max_length=100, blank=True, null=True)
    
    store_number = models.CharField(max_length=64, blank=True, null=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)

    mo_code = models.CharField(max_length=64)
    zip_code = models.CharField(max_length=10)
    county = models.CharField(max_length=100, blank=True, null=True)
    
    gps_coordinates = models.TextField(blank=True, null=True)
    field_location_notes = models.TextField(blank=True, null=True)
    barriers_to_inspection = models.TextField(blank=True, null=True)
    
    site_contact_name = models.CharField(max_length=255, blank=True, null=True)
    site_contact_phone = models.CharField(max_length=30, blank=True, null=True)
    site_contact_email = models.EmailField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'locations'
        verbose_name_plural = "Locations"
    
    def get_parent(self):
        return self.business

    @staticmethod
    def get_add_url():
        return "add_location"

    def __str__(self):
        return f"{self.business.business_name} - {self.city}"


class Licenses(models.Model):
    license_id = models.AutoField(primary_key=True)
    location = models.ForeignKey(Locations, on_delete=models.CASCADE)
    
    license_period_start = models.DateField()
    license_period_end = models.DateField()
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_method = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'licenses'
        verbose_name_plural = "Licenses"
        unique_together = ('location', 'license_period_start')

    def __str__(self):
        return f"Lic {self.license_period_end.year} - {self.location}"


class ComplianceAgreements(models.Model):
    agreement_id = models.AutoField(primary_key=True)
    business = models.ForeignKey(Businesses, on_delete=models.CASCADE)
    agreement_number = models.CharField(max_length=100, unique=True)
    articles_covered = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'compliance_agreements'
        verbose_name_plural = "Compliance Agreements"

    def get_parent(self):
        return self.business

    @staticmethod
    def get_add_url():
        return "add_compliance_agreement"

    def __str__(self):
        return self.agreement_number


class Inspections(models.Model):
    inspection_id = models.AutoField(primary_key=True)
    location = models.ForeignKey(Locations, on_delete=models.CASCADE)
    
    inspected_by = models.CharField(max_length=255, blank=True, null=True)
    inspection_date = models.DateField(default=timezone.now)
    additional_inspection_date = models.DateField(blank=True, null=True)
    
    passes_inspection = models.BooleanField(default=True)
    verbal_report = models.BooleanField(default=False)
    
    infestation_summary = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    
    samples_taken_pram = models.BooleanField(default=False)
    sample_number = models.CharField(max_length=256, blank=True, null=True)
    trace_back = models.TextField(blank=True, null=True)
    trace_forward = models.TextField(blank=True, null=True)
    scn_samples = models.BooleanField(default=False)

    class Meta:
        db_table = 'inspections'
        verbose_name_plural = "Inspections"

    def __str__(self):
        return f"{self.inspection_date} - {self.location}"


class InspectionFindings(models.Model):
    finding_id = models.AutoField(primary_key=True)
    inspection = models.ForeignKey(Inspections, on_delete=models.CASCADE, related_name='findings')
    pest = models.ForeignKey(Pests, on_delete=models.PROTECT)
    
    plant_name = models.CharField(max_length=255, blank=True, null=True)
    location_description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'inspection_findings'
        verbose_name_plural = "Inspection Findings"

    def __str__(self):
        return f"{self.pest} found on {self.plant_name}"
