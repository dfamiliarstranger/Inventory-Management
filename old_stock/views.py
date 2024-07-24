from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Old_Stock, Product
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_protect
from decimal import Decimal
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.utils import timezone



# Create your views here.
@login_required
@csrf_protect
def old_stock_create_view(request):
    products = Product.objects.all()
    
    if request.method == 'POST':
        # Retrieve data from POST request
        product_id = request.POST.get('product')
        unit = request.POST.get('unit')
        created_at_str = request.POST.get('created_at')
        price = request.POST.get('price')

        # Validate data
        if not product_id or not unit or not price or not created_at_str:
            messages.error(request, 'All fields are required.')
            return render(request, 'old_stock_form.html', {'products': products})

        # Ensure the product exists
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            messages.error(request, 'Invalid product.')
            return render(request, 'old_stock_form.html', {'products': products})

        try:
            # Convert unit to Decimal and validate
            unit = Decimal(unit)
        except ValueError:
            messages.error(request, 'Unit must be a decimal number.')
            return render(request, 'old_stock_form.html', {'products': products})

        try:
            # Parse created_at string to datetime
            created_at = datetime.strptime(created_at_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            messages.error(request, 'Created at must be in the format YYYY-MM-DD HH:MM:SS.')
            return render(request, 'old_stock_form.html', {'products': products})

        # Calculate quantity
        if product.quantity and product.quantity != 0:
            quantity = unit / Decimal(product.quantity)
        else:
            quantity = Decimal(0)

        # Create Old_Stock instance
        old_stock = Old_Stock.objects.create(
            product=product,
            unit=unit,
            quantity=quantity,
            created_at=created_at,
            price=price
        )
        old_stock.save()
        messages.success(request, 'Old Stock created successfully.')
        # Redirect to old stock list view upon successful creation
        return redirect('old_stock')

    # Render the form template for GET requests
    return render(request, 'old_stock/old_stock_form.html', {'products': products})



@login_required
def update_old_stock(request, oid):
    old_stock = get_object_or_404(Old_Stock, oid=oid)
    products = Product.objects.all()

    if request.method == 'POST':
        product_id = request.POST.get('product')
        unit = request.POST.get('unit')
        created_at_str = request.POST.get('created_at')
        price = request.POST.get('price')
        # Validate and update old_stock
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            messages.error(request, 'Invalid product.')
            return render(request, 'old_stock/update_old_stock.html', {'old_stock': old_stock})

        try:
            if unit:
                unit = Decimal(unit.replace(',', ''))  # Remove any commas if present
            else:
                raise ValueError('Unit cannot be empty.')
        except ValueError:
            messages.error(request, 'Unit must be a decimal number.')
            return render(request, 'old_stock/update_old_stock.html', {'old_stock': old_stock})

        try:
            created_at = timezone.datetime.strptime(created_at_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            messages.error(request, 'Created at must be in the format YYYY-MM-DDTHH:MM.')
            return render(request, 'old_stock/update_old_stock.html', {'old_stock': old_stock})

        if product.quantity and product.quantity != 0:
            quantity = unit / Decimal(product.quantity)
        else:
            quantity = Decimal(0)

        # Update old_stock instance
        old_stock.product = product
        old_stock.unit = unit
        old_stock.quantity = quantity
        old_stock.created_at = created_at
        old_stock.price = price
        old_stock.save()

        messages.success(request, 'Old Stock updated successfully.')
        return redirect('stock_list')

    return render(request, 'old_stock/update_old_stock.html', {'old_stock': old_stock,'products':products})



@login_required
def delete_old_stock(request, pk):
    old_stock = get_object_or_404(Old_Stock, pk=pk)

    if request.method == 'POST':
        old_stock.delete()
        messages.success(request, 'Old Stock deleted successfully.')
        return redirect('stock_list')

    return render(request, 'stock_list', {'old_stock': old_stock})


@login_required
def old_stock(request):
    old_stock = Old_Stock.objects.all().order_by('created_at')

    paginator = Paginator(old_stock, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'old_stock/old_stock.html', {'page_obj': page_obj})