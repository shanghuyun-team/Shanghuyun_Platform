from django.shortcuts import render

# Create your views here.
def home(request):
    """
    Render the vendor dashboard page.
    """
    return render(request, 'Dashboard/home/index.html')

def add_product(request):
    """
    Render the add product page.
    """
    return render(request, 'Dashboard/home/add_product.html')