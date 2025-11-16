from django import forms
from django.forms import inlineformset_factory
from .models import Businesses, Locations

class BusinessForm(forms.ModelForm):
    """
    Add business Form
    """
    class Meta:
        model = Businesses
        fields = [
            'business_name', 
            'main_contact_name', 
            'main_contact_email', 
            'main_contact_phone',
        ]

LocationFormSet = inlineformset_factory(
    Businesses,       
    Locations,        
    fields=(         
        'address', 
        'city', 
        'state', 
        'zip_code'
    ),
    extra=1,          
    can_delete=True   
)
