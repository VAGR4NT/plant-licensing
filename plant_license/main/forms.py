from django import forms
from dal import autocomplete
from .models import Businesses, Suppliers, BusinessTypes, PlantTypes, SellingSeasons, ShippingRegions, Locations, ComplianceAgreements

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, HTML, Field, Submit, Row, Column

class BaseBusinessForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        
        self.helper.layout = Layout(
            
            HTML("<div class='section-title'>Core Information</div>"),
            Div(
                Div('business_name', css_class='half-width'),
                Div('dba_business_name', css_class='half-width'),
                css_class='form-row'
            ),
            Div(
                Div('formerly_known_as', css_class='half-width'),
                Div('entity_type', css_class='hidden'),
                css_class='form-row'
            ),

            HTML("<div class='section-title'>Address</div>"),
            Div(
                'mo_address',
                css_class='form-row full-width'
            ),
            Div(
                'mo_city', 'mo_state', 'mo_zip',
                css_class='form-row three-col'
            ),

            HTML("<div class='section-title'>Primary Contact</div>"),
            Div(
                'main_contact_name', 
                'main_contact_phone', 
                'main_contact_email',
                css_class='form-row three-col'
            ),
            
            HTML("<div class='section-title'>Secondary Contact / Details</div>"),
            Div(
                'main_contact_alt_phone',
                'main_contact_alt_email',
                'main_contact_fax',
                css_class='form-row three-col'
            ),

            HTML("<div class='section-title'>Administrative Details</div>"),
            Div(
                Div('priority_rank', css_class='half-width'),
                Div('class_code', css_class='half-width'),
                css_class='form-row'
            ),
            
            Div(
                Div('is_interstate_shipper', css_class='flag-item'),
                Div('wants_email_renewal', css_class='flag-item'),
                Div('wants_email_license', css_class='flag-item'),
                Div('wants_labels', css_class='flag-item'),
                css_class='checkbox-grid',
                style="align-items: center; margin-top: 10px; border: 1px; border: 1px solid #ccc; padding: 10px;"
            ),
            Div(
                'num_labels',
                css_class='form-row full-width',
                style="margin-top: 10px;"
            ),


            HTML("<div class='section-title'>Suppliers</div>"),
            Div(
                'suppliers',
                css_class='form-row full-width'
            ),
        )

    class Meta:
        model = Businesses
        fields = [
            'business_name', 'dba_business_name', 'entity_type',
            'mo_address', 'mo_city', 'mo_state', 'mo_zip',
            'main_contact_name', 'main_contact_phone', 'main_contact_email',
            'main_contact_alt_phone', 'main_contact_fax', 'main_contact_alt_email',
            'formerly_known_as', 'priority_rank', 'class_code',
            'is_interstate_shipper', 'wants_email_renewal', 'wants_email_license',
            'wants_labels', 'num_labels',
            'suppliers'
        ]
        widgets = {
            'deletion_reason': forms.Textarea(attrs={'rows': 2}),
            
            'suppliers': autocomplete.ModelSelect2Multiple(
                url='supplier-autocomplete', 
                attrs={'style': 'width: 100%;', 'data-placeholder': 'Search suppliers...'}
            )
        }


class DealerForm(BaseBusinessForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['entity_type'].initial = 'Dealer'

class NurseryForm(BaseBusinessForm):
    business_types = forms.ModelMultipleChoiceField(
        queryset=BusinessTypes.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    plant_types = forms.ModelMultipleChoiceField(
        queryset=PlantTypes.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    selling_seasons = forms.ModelMultipleChoiceField(
        queryset=SellingSeasons.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    shipping_regions = forms.ModelMultipleChoiceField(
        queryset=ShippingRegions.objects.all(),
        widget=forms.SelectMultiple(attrs={'style': 'width: 100%; height: 100px;'}),
        required=False
    )

    class Meta(BaseBusinessForm.Meta):
        # Append the Nursery-only fields to the list
        fields = BaseBusinessForm.Meta.fields + [
            'acreage', 'business_types', 'plant_types', 
            'selling_seasons', 'shipping_regions'
        ]
        widgets = BaseBusinessForm.Meta.widgets.copy()
        widgets['acreage'] = forms.NumberInput(attrs={'step': '0.01'})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["entity_type"].initial = 'Nursery'

        # APPEND TO LAYOUT
        # We add the "Nursery Specifics" section to the bottom of the base layout
        self.helper.layout.append(
            HTML("<div class='section-title' style='color: #2e7d32;'>Nursery Specifics</div>")
        )
        
        self.helper.layout.append(
            Div('acreage', css_class='form-row full-width')
        )

        # Multi-Selects in scrolling boxes
        self.helper.layout.append(
            Div(
                Div(
                    HTML("<strong>Business Types</strong>"),
                    Div('business_types', css_class='checkbox-grid', style="max-height: 200px; overflow-y: auto; border: 1px solid #ccc; padding: 10px;"),
                ),
                Div(
                    HTML("<strong>Plants Sold</strong>"),
                    Div('plant_types', css_class='checkbox-grid', style="max-height: 200px; overflow-y: auto; border: 1px solid #ccc; padding: 10px;"),
                ),
                Div(
                    HTML("<strong>Selling Seasons</strong>"),
                    Div('selling_seasons', css_class='checkbox-grid', style="max-height: 200px; overflow-y: auto; border: 1px solid #ccc; padding: 10px;"),
                ),
                css_class='form-row three-col'
            )
        )
        
        self.helper.layout.append(
             Div(
                HTML("<strong>Shipping Regions</strong>"),
                Div('shipping_regions'),
                css_class='form-row full-width'
            )
        )


class LocationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.business_id = kwargs.pop('parent_id', None)
        super().__init__(*args, **kwargs)
        
        if self.business_id:
            self.fields['business'].initial = Businesses.objects.get(pk=self.business_id)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
       
        self.fields['business'].disabled = True

        self.helper.layout = Layout(
            
            HTML("<div class='section-title'>Core Information</div>"),
            Div(
                Div('business'),
                Div('legacy_license_id'),
                Div('store_number'),
                Div('mo_code'),
            ),
            Div(
                Div('address', css_class='half-width'),
                Div('city', css_class='half-width'),
                Div('state', css_class='half-width'),
                css_class='form-row'
            ),
            Div(
                Div('zip_code', css_class='half-width'),
                Div('county', css_class='half-width'),
                css_class='form-row'
            ),

            HTML("<div class='section-title'>Primary Contact</div>"),
            Div(
                'site_contact_name', 
                'site_contact_phone', 
                'site_contact_email',
                css_class='form-row three-col'
            ),
            
            HTML("<div class='section-title'>Details</div>"),
            Div(
                Div('gps_coordinates'),
                Div('field_location_notes'),
                Div('barriers_to_inspection'),
                css_class='form-row three-col'
            ),
        )

    class Meta:
        model = Locations
        fields = [
            'business', 'legacy_license_id', 'store_number', 'mo_code',
            'address', 'city', 'state', 'zip_code', 'county', 'gps_coordinates',
            'field_location_notes', 'barriers_to_inspection', 'site_contact_name', 
            'site_contact_phone', 'site_contact_email'
        ]
        widgets = {
            
        }


class ComplianceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.business_id = kwargs.pop('parent_id', None)
        super().__init__(*args, **kwargs)
        
        if self.business_id:
            self.fields['business'].initial = Businesses.objects.get(pk=self.business_id)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
       
        self.fields['business'].disabled = True

        self.helper.layout = Layout(
            
            HTML("<div class='section-title'>Agreement</div>"),
            Div(
                Div('business'), 
                Div('agreement_number'),
                Div('articles_covered'),
            ),
        )

    class Meta:
        model = ComplianceAgreements
        fields = [
            'business', 'agreement_number', 'articles_covered'
        ]
        widgets = {
            
        }

class SupplierForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
       
        self.helper.form_action = ""

        self.helper.layout = Layout(
            
            HTML("<div class='section-title'>Supplier</div>"),
            Div(
                Div('supplier_name'),
                Div('address'),
                Div('city'),
                Div('state'),
                Div('zip_code'),
            )
        )

    class Meta:
        model = Suppliers
        fields = [
            'supplier_name', 'address', 'city', 'state', 'zip_code'
        ]
        widgets = {
            
        }


