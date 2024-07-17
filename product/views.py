from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.shortcuts import render, redirect,  get_object_or_404
from django.http import HttpResponseBadRequest
from django.utils import timezone

from .models import Product, Color, Product_type


@login_required
# PRODUCT VIEWS
def product_list_create(request):
    products = Product.objects.all()
    product_names = Product.PRODUCT_NAME
    product_units = Product.PRODUCT_UNIT
    type = Product_type.objects.all()
    color = Color.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        type_id = request.POST.get('type')
        color_id = request.POST.get('color')
        size = request.POST.get('size')
        unit = request.POST.get('unit')
        
        quantity = request.POST.get('quantity')
        

        # Convert size, quantity, and unit_ratio to proper types
        try:
            size = float(size) if size else None
            unit = unit if size else None
            quantity = float(quantity) if quantity else 1
            
             # Check if a similar product already exists
            if Product.objects.filter(name=name, type_id=type_id, color_id=color_id, size=size, unit=unit).exists():
                messages.error(request, 'Product already exists.')
                return render(request, 'create_product.html', {
                    'products': products,
                    'color': color,
                    'type': type,
                    'product_names': product_names,
                    'product_units': product_units
                })

            # Retrieve type_obj and color_obj if provided
            type_obj = get_object_or_404(Product_type, id=type_id) if type_id else None
            color_obj = get_object_or_404(Color, id=color_id) if color_id else None
            
        except ValueError:
            # Handle the error if conversion fails
            messages.error(request, 'create_product.html', {
                'error': 'Invalid input. Please enter valid numbers for quantity, and unit',
                'products': products,
                
                'product_names': product_names,
                'product_units': product_units
            })
        except IntegrityError as ie:
            messages.error(request, f'Database error: {str(ie)}')
         # Create and save the product
        try:
            product = Product(
                name=name,
                type=type_obj,
                size=size,
                color=color_obj,
                unit=unit,
                quantity=quantity,
                
            )
            product.save()
            messages.success(request, 'Product created successfully.')
            return redirect('create_product')  # Redirect to your desired URL after successful creation
        except Exception as e:
            messages.error(request, f'Error creating product: {str(e)}')
    
    return render(request, 'product/create_product.html', {
        'products': products,
        'color': color,
        'type': type,
        'product_names': product_names,
        'product_units': product_units
    })

@login_required
def product_update(request, product_id):
    # Retrieve the product object
    product_names = Product.PRODUCT_NAME
    product_units = Product.PRODUCT_UNIT
    product = get_object_or_404(Product, pk=product_id)
    type = Product_type.objects.all()
    color = Color.objects.all()
    
    if request.method == 'POST':
        # Update the product with data from POST request
        product.name = request.POST.get('name')
        product.type_id = request.POST.get('type')
        product.color_id = request.POST.get('color')
        product.size = float(request.POST.get('size')) if request.POST.get('size') else None
        product.unit = request.POST.get('unit')
        product.quantity = float(request.POST.get('quantity')) if request.POST.get('quantity') else None
        
        try:
            product.save()  # Save the updated product
            messages.success(request, 'Product updated successfully.') 
            return redirect('create_product')  # Redirect to detail view or any other page
        except ValueError:
            messages.error(request, 'Failed to update product. Please try again.') 
            # Handle validation errors or other exceptions
            pass  # Add your error handling here if needed
    
    # Render the edit form with initial data
    return render(request, 'product/update_product.html', {'product': product, 'type': type, 'color': color,         'product_names': product_names, 'product_units': product_units})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('product_list')  # Redirect to product list or another page after deletion

    return redirect(request, 'product_list', {'product': product})

@login_required
def product_list(request):
    products = Product.objects.all().order_by('name')

    paginator = Paginator(products, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'product/ex.html', {'page_obj': page_obj})