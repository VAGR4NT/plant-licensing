from django.shortcuts import render
from django.http import HttpResponse
from .models import Suppliers
from django.db import connection 

def home_view(request):
    
    total_posts = Suppliers.objects.count()

    context = {
        'number_of_suppliers': total_posts *2,
    }   

    return render(request, "main/index.html", context)

def specific_view(request):
    query = request.GET.get('q', '')
    
    category_id = request.GET.get('category')
    
    if category_id:
        category = get_object_or_404(Category, pk=category_id)
        search_pool = Post.objects.filter(category=category)
    else:
        category = None
        search_pool = Post.objects.all()

    posts = Post.objects.none()
    if query:
        posts = search_pool.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    context = {
        'query': query,
        'posts': posts,
        'selected_category': category, # Pass the category to the template
    }
    
    return render(request, 'my_app/search_results.html', context)

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



