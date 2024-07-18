from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Purchase, Product, Supplier, Inventory
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_protect

@login_required
@csrf_protect
def purchase_create_view(request):
    product = Product.objects.all()
    supplier = Supplier.objects.all()
    if request.method == 'POST':
        # Retrieve data from POST request
        product_id = request.POST.get('product')
        supplier_id = request.POST.get('supplier')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        total = request.POST.get('total')

        # Validate data
        if not product_id or not supplier_id or not quantity  or not price or not total:
            messages.error(request, 'All fields are required.')
            return render(request, 'purchase/purchase_form.html')

        # Ensure the product and supplier exist
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            messages.error(request, 'Invalid product.')
            return render(request, 'purchase/purchase_form.html')

        try:
            supplier = Supplier.objects.get(pk=supplier_id)
        except Supplier.DoesNotExist:
            messages.error(request, 'Invalid supplier.')
            return render(request, 'purchase/purchase_form.html')

        try:
            # Convert numeric fields to appropriate types and validate
            quantity = float(quantity)
            price = float(price)
            total = float(total)
        except ValueError:
            messages.error(request, 'Quantity, price, and total must be numeric.')
            return render(request, 'purchase/purchase_form.html')

        # Create Purchase instance
        purchase = Purchase.objects.create(
            product=product,
            supplier=supplier,
            quantity=quantity,
            price=price,
            total=total
        )
        purchase.save()
        messages.success(request, 'Purchase created successfully.')
        # Redirect to purchase list view upon successful creation
        return redirect('purchase_list')

    # Render the form template for GET requests
    return render(request, 'purchase/purchase_form.html', {'product': product,
        'supplier': supplier,})



def update_purchase(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    product = Product.objects.all()
    supplier = Supplier.objects.all()

    if request.method == 'POST':
        product_id = request.POST.get('product')
        supplier_id = request.POST.get('supplier')
        quantity = request.POST.get('quantity')
        unit = request.POST.get('unit')
        price = request.POST.get('price')
        total = request.POST.get('total')
        

        # Add validation logic here
        try:
            quantity = float(quantity)
            unit = float(unit)
            price = float(price)
            total = float(total)
        except ValueError:
            messages.error(request, 'Invalid input for quantity. Please enter a valid number.')
            return render(request, 'purchase/update_purchase.html', {'purchase': purchase})

        # Update the purchase instance
        purchase.product_id = product_id
        purchase.supplier_id = supplier_id
        purchase.quantity = quantity
        purchase.unit = unit
        purchase.price = price
        purchase.total = total
        purchase.save()  # Save the updated product
        messages.success(request, 'Purchase updated successfully.') 
        return redirect('purchase_form')  # Redirect to detail view or any other page

    return render(request, 'purchase/update_purchase.html', {'purchase': purchase,'product': product,
        'supplier': supplier})


@login_required
def purchase_list(request):
    purchase = Purchase.objects.all().order_by('created_at')

    paginator = Paginator(purchase, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'purchase/index.html', {'page_obj': page_obj})


@login_required
def purchase_delete(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)

    if request.method == 'POST':
        purchase.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('purchase_list')  # Redirect to product list or another page after deletion

    return redirect(request, 'purchase_list', {'purchase': purchase})


##### Inventory   ###

@login_required
def inventory_list(request):
    inventory = Inventory.objects.all()

    paginator = Paginator(inventory, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'inventory/index.html', {'page_obj': page_obj})