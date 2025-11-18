# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


# for generating .eml files
class EmailTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=300)
    body = models.TextField()

    def __str__(self):
        return self.name


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = "auth_group"


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey("AuthPermission", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "auth_group_permissions"
        unique_together = (("group", "permission"),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey("DjangoContentType", models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "auth_permission"
        unique_together = (("content_type", "codename"),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "auth_user"


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "auth_user_groups"
        unique_together = (("user", "group"),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "auth_user_user_permissions"
        unique_together = (("user", "permission"),)


class BusinessPlantTypes(models.Model):
    pk = models.CompositePrimaryKey("business_id", "plant_type_id")
    business = models.ForeignKey("Businesses", models.DO_NOTHING)
    plant_type = models.ForeignKey("PlantTypes", models.DO_NOTHING)
    is_through_table = True

    class Meta:
        managed = False
        db_table = "business_plant_types"


class BusinessSellingSeasons(models.Model):
    pk = models.CompositePrimaryKey("business_id", "season_id")
    business = models.ForeignKey("Businesses", models.DO_NOTHING)
    season = models.ForeignKey("SellingSeasons", models.DO_NOTHING)
    is_through_table = True

    class Meta:
        managed = False
        db_table = "business_selling_seasons"


class BusinessShippingRegions(models.Model):
    pk = models.CompositePrimaryKey("business_id", "region_id")
    business = models.ForeignKey("Businesses", models.DO_NOTHING)
    region = models.ForeignKey("ShippingRegions", models.DO_NOTHING)
    is_through_table = True

    class Meta:
        managed = False
        db_table = "business_shipping_regions"


class BusinessSuppliers(models.Model):
    pk = models.CompositePrimaryKey("business_id", "supplier_id")
    business = models.ForeignKey(
        "Businesses", models.DO_NOTHING, related_name="supplier_links"
    )
    supplier = models.ForeignKey(
        "Suppliers", models.DO_NOTHING, related_name="business_links"
    )
    is_through_table = True

    class Meta:
        managed = False
        db_table = "business_suppliers"


class BusinessTypeMap(models.Model):
    pk = models.CompositePrimaryKey("business_id", "type_id")
    business = models.ForeignKey("Businesses", models.DO_NOTHING)
    type = models.ForeignKey("BusinessTypes", models.DO_NOTHING)
    is_through_table = True

    class Meta:
        managed = False
        db_table = "business_type_map"


class BusinessTypes(models.Model):
    type_id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=256, blank=True, null=True)
    is_through_table = True

    class Meta:
        managed = False
        db_table = "business_types"


class Businesses(models.Model):
    business_id = models.AutoField(primary_key=True)
    entity_type = models.CharField(max_length=20, blank=True, null=True)
    business_name = models.CharField(max_length=256, blank=True, null=True)
    dba_business_name = models.CharField(max_length=256, blank=True, null=True)
    mo_address = models.CharField(max_length=256, blank=True, null=True)
    mo_city = models.CharField(max_length=256, blank=True, null=True)
    mo_state = models.CharField(max_length=256, blank=True, null=True)
    mo_zip = models.CharField(max_length=256, blank=True, null=True)
    class_field = models.CharField(
        db_column="class", max_length=1, blank=True, null=True
    )  # Field renamed because it was a Python reserved word.
    acreage = models.FloatField(blank=True, null=True)
    is_deleted = models.BooleanField(blank=True, null=True)
    date_deleted = models.DateField(blank=True, null=True)
    deletion_reason = models.CharField(max_length=512, blank=True, null=True)
    date_applied = models.DateField(blank=True, null=True)
    priority_rank = models.IntegerField(blank=True, null=True)
    is_interstate_shipper = models.BooleanField(blank=True, null=True)
    main_contact_name = models.CharField(max_length=256, blank=True, null=True)
    main_contact_phone = models.CharField(max_length=256, blank=True, null=True)
    main_contact_email = models.CharField(max_length=256, blank=True, null=True)
    wants_email_renewal = models.BooleanField(blank=True, null=True)
    wants_email_license = models.BooleanField(blank=True, null=True)
    wants_labels = models.BooleanField(blank=True, null=True)
    num_labels = models.IntegerField(blank=True, null=True)

    suppliers = models.ManyToManyField(
        "Suppliers", through="BusinessSuppliers", related_name="businesses"
    )
    plant_types = models.ManyToManyField(
        "PlantTypes", through="BusinessPlantTypes", related_name="businesses"
    )
    selling_seasons = models.ManyToManyField(
        "SellingSeasons", through="BusinessSellingSeasons", related_name="businesses"
    )
    shipping_regions = models.ManyToManyField(
        "ShippingRegions", through="BusinessShippingRegions", related_name="businesses"
    )

    def __str__(self):
        return (self.business_name or "").title()

    class Meta:
        managed = False
        db_table = "businesses"


class ComplianceAgreements(models.Model):
    agreement_id = models.AutoField(primary_key=True)
    business = models.ForeignKey(Businesses, models.DO_NOTHING, blank=True, null=True)
    agreement_number = models.TextField(blank=True, null=True)
    articles_covered = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Agreement with {self.business}"

    class Meta:
        managed = False
        db_table = "compliance_agreements"


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey(
        "DjangoContentType", models.DO_NOTHING, blank=True, null=True
    )
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "django_admin_log"


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "django_content_type"
        unique_together = (("app_label", "model"),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "django_migrations"


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "django_session"


class Licenses(models.Model):
    license_id = models.AutoField(primary_key=True)
    location = models.ForeignKey(
        "Locations", on_delete=models.CASCADE, blank=True, null=True
    )
    license_year = models.IntegerField(blank=True, null=True)
    check_number = models.CharField(max_length=256, blank=True, null=True)
    license_number = models.IntegerField(unique=True, blank=True, null=True)

    def __str__(self):
        return f"License for {self.location}"

    class Meta:
        managed = False
        db_table = "licenses"


class Locations(models.Model):
    location_id = models.AutoField(primary_key=True)
    business = models.ForeignKey(Businesses, models.DO_NOTHING, blank=True, null=True)
    store_number = models.CharField(max_length=64, blank=True, null=True)
    mo_code = models.CharField(max_length=64, blank=True, null=True)
    address = models.CharField(max_length=512, blank=True, null=True)
    city = models.CharField(max_length=256, blank=True, null=True)
    state = models.CharField(max_length=128, blank=True, null=True)
    zip_code = models.CharField(max_length=32, blank=True, null=True)
    county = models.CharField(max_length=128, blank=True, null=True)
    gps_coordinates = models.TextField(blank=True, null=True)
    field_location_notes = models.TextField(blank=True, null=True)
    barriers_to_inspection = models.TextField(blank=True, null=True)
    site_contact_name = models.CharField(max_length=256, blank=True, null=True)
    site_contact_phone = models.CharField(max_length=32, blank=True, null=True)
    site_contact_email = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return f"{self.address}, {self.city}, {self.state} {self.zip_code}"

    class Meta:
        managed = False
        db_table = "locations"


class Pests(models.Model):
    pest_id = models.AutoField(primary_key=True)
    pest_name = models.TextField(unique=True)

    class Meta:
        managed = False
        db_table = "pests"


class PlantTypes(models.Model):
    plant_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "plant_types"


class SellingSeasons(models.Model):
    season_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "selling_seasons"


class ShippingRegions(models.Model):
    region_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "shipping_regions"


class Suppliers(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    supplier_name = models.CharField(max_length=256, blank=True, null=True)
    address = models.CharField(max_length=512, blank=True, null=True)
    city = models.CharField(max_length=256, blank=True, null=True)
    state = models.CharField(max_length=128, blank=True, null=True)
    zip_code = models.CharField(max_length=18, blank=True, null=True)

    def __str__(self):
        return (self.supplier_name or "").title()

    class Meta:
        managed = False
        db_table = "suppliers"
