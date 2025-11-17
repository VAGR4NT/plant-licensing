from django import forms
from django.forms import inlineformset_factory
from .models import Businesses, Locations, Licenses
from dal import autocomplete

class BusinessForm(forms.ModelForm):

    class Meta:
        model = Businesses
        fields = [
            'business_name', 
            'main_contact_name', 
            'main_contact_email', 
            'main_contact_phone',
            'suppliers'
        ]

        widgets = {
            'suppliers': autocomplete.ModelSelect2Multiple(
            url='supplier-autocomplete'
            )} 

class LocationForm(forms.ModelForm):

    class Meta:
        model = Locations
        fields = [        
            'address', 
            'city', 
            'state', 
            'zip_code'
        ]


LocationFormSet = inlineformset_factory(
    Businesses,       
    Locations,        
    form=LocationForm,  
    extra=1,          
    can_delete=False
    )

LocationLicenseFormSet = inlineformset_factory(
    Locations,   
    Licenses,    
    fields=(     
        'check_number',
        #'license_period_start',
        #'license_period_end',
        #'amount_due',
        #'payment_method'
    ),
    extra=1,
    can_delete=False
)



