from django.shortcuts import render
from django.http import HttpResponse
from .models import Suppliers
from .models import Businesses
from django.db import connection 

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


def view_db_view(request):
    return render(request, "main/view/index.html")


def generate_forms_view(request):
    return render(request, "main/generate-forms/index.html")


def update_view(request):
    return render(request, "main/update/index.html")


def user_info_view(request):
    return render(request, "main/user-info/index.html")



