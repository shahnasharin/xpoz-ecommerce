from django.shortcuts import render
from store.models import Product

def home(request):
    products = Product.objects.all().filter(is_available=True)
    print(products[1].get_url())
    context = {
        'products': products,
       
    }
    return render(request,'home.html', context)