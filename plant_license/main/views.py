from django.shortcuts import render
from django.http import HttpResponse
from .models import Suppliers
from .models import Businesses
from django.db import connection 

import csv
from django.http import HttpResponse

def home_view(request):
    
    total_posts = Suppliers.objects.count()

    context = {
        'number_of_suppliers': total_posts *2,
    }   

    return render(request, "main/index.html", context)

def specific_view(request, category):
    ALLOWED_SEARCH_FIELDS = ['business_name', 'business_id']

    if category not in ALLOWED_SEARCH_FIELDS:
        raise Http404("Invalid search category")

    query = request.GET.get('q')
    businesses = Businesses.objects.none()

    if query:
        filter_kwargs = {f"{category}__icontains": query}
        businesses = Businesses.objects.filter(**filter_kwargs)

    context = {
        'businesses': businesses,
        'category': category, 
        'query': query,
    } 
    
    return render(request, 'main/view/specific_view.html', context)

def direct_access_view(request):
    return render(request, "main/direct-access/index.html")

def export_data_as_csv(request):
    """
    A view to export all SampleData objects as a CSV file.
    """
    
    # Create the HttpResponse object with the appropriate CSV header.
    # This tells the browser to treat the response as a file to be downloaded.
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="data.csv"'},
    )

    # Get all data from your model
    # This assumes your model is SampleData. Replace with your actual model.
    queryset = Businesses.objects.all()
    
    # Check if there is any data to write
    if not queryset.exists():
        response.write("No data found.")
        return response

    # Get the model's field names
    # We use _meta.fields to get all field objects
    # and then get the name for each field.
    field_names = [field.name for field in Businesses._meta.fields]

    # Create a CSV writer object using the response as the file
    writer = csv.writer(response)

    # Write the header row
    writer.writerow(field_names)

    # Iterate over the queryset and write each row to the CSV
    for obj in queryset:
        # Create a list of values for the current object
        row = [getattr(obj, field) for field in field_names]
        writer.writerow(row)

    return response


def view_db_view(request):
    return render(request, "main/view/index.html")


def generate_forms_view(request):
    return render(request, "main/generate-forms/index.html")


def update_view(request):
    return render(request, "main/update/index.html")


def user_info_view(request):
    return render(request, "main/user-info/index.html")





