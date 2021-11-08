from django.shortcuts import redirect, render
from store.models import Product

def home(request):
    proudcts = Product.objects.all().filter(is_popular=True)
    dealoftheday = Product.objects.all().filter(dealofday=True)
    brass_deties = Product.objects.all().filter(category=10)
    instruments = Product.objects.all().filter(category=11)
    context = {
        'products': proudcts,
        'dealoftheday': dealoftheday,
        'brassdeties': brass_deties,
        'instruments': instruments,
    }
    return render(request, 'home.html', context)

def ata(request):
    return render(request, 'about.html', {})

def shashtradan(request):
    return render(request, 'shashtradan.html', {})