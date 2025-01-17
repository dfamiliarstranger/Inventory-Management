from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Inventory, Sale, Customer
from purchase.models import Inventory
from product.models import Product
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_protect
from decimal import Decimal

@login_required
@csrf_protect
def sale_create_view(request):
    products = Product.objects.all()
    customers = Customer.objects.all()
    if request.method == 'POST':
        # Retrieve data from POST request
        product_id = request.POST.get('product')
        customer_id = request.POST.get('customer')
        unit = request.POST.get('unit')
        price = request.POST.get('price')
        total = request.POST.get('total')
        created_at = request.POST.get('date')

        # Validate data
        if not product_id or not customer_id or not unit or not price or not total:
            messages.error(request, 'All fields are required.')
            return render(request, 'sale/sale_form.html', {'products': products, 'customers': customers})

        # Ensure the product and customer exist
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            messages.error(request, 'Invalid product.')
            return render(request, 'sale/sale_form.html', {'products': products, 'customers': customers})

        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            messages.error(request, 'Invalid customer.')
            return render(request, 'sale/sale_form.html', {'products': products, 'customers': customers})

        try:
            # Convert numeric fields to appropriate types and validate
            unit = Decimal(unit)
            price = Decimal(price)
            total = Decimal(total)
        except ValueError:
            messages.error(request, 'Unit, price, and total must be numeric.')
            return render(request, 'sale/sale_form.html', {'products': products, 'customers': customers})

        try:
            # Ensure the product exists in the inventory
            inventory_item = Inventory.objects.get(product=product)

            # Check if there is enough inventory to make the sale
            if unit > inventory_item.unit:
                messages.error(request, 'Not enough inventory to make this sale.')
                return render(request, 'sale/sale_form.html', {'products': products, 'customers': customers})

            # Calculate the quantity based on the unit
            quantity = unit / inventory_item.unit

            # Create Sale instance
            sale = Sale.objects.create(
                product=product,
                customer=customer,
                quantity=quantity,
                unit=unit,
                price=price,
                total=total,
                created_at=created_at
            )

            # Update inventory
            
            inventory_item.unit -= unit
            inventory_item.save()

            messages.success(request, 'Sale created successfully.')
            # Redirect to sale list view upon successful creation
            return redirect('sale_list')
        except Inventory.DoesNotExist:
            messages.error(request, 'Inventory item for the selected product does not exist.')
            return render(request, 'sale/sale_form.html', {'products': products, 'customers': customers})

    # Render the form template for GET requests
    return render(request, 'sale/sale_form.html', {'products': products, 'customers': customers})


@login_required
def sale_list(request):
    sale = Sale.objects.all().order_by('-created_at')  # Order by descending
    paginator = Paginator(sale, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'sale/index.html', {'page_obj': page_obj})



@login_required
def sale_delete(request, pk):
    sale = get_object_or_404(Sale, pk=pk)

    if request.method == 'POST':
        sale.delete()
        messages.success(request, 'Sales deleted successfully.')
        return redirect('sale_list')  # Redirect to product list or another page after deletion

    return redirect(request, 'sale_list', {'sale': sale})




@login_required
@csrf_protect
def sale_update_view(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    products = Product.objects.all()
    customers = Customer.objects.all()

    if request.method == 'POST':
        # Retrieve data from POST request
        product_id = request.POST.get('product')
        customer_id = request.POST.get('customer')
        unit = request.POST.get('unit')
        price = request.POST.get('price')
        total = request.POST.get('total')
        created_at = request.POST.get('date')

        # Validate data
        if not product_id or not customer_id or not unit or not price or not total:
            messages.error(request, 'All fields are required.')
            return render(request, 'sale/sale_update.html', {'products': products, 'customers': customers, 'sale': sale})

        # Ensure the product and customer exist
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            messages.error(request, 'Invalid product.')
            return render(request, 'sale/sale_update.html', {'products': products, 'customers': customers, 'sale': sale})

        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            messages.error(request, 'Invalid customer.')
            return render(request, 'sale/sale_update.html', {'products': products, 'customers': customers, 'sale': sale})

        try:
            # Convert numeric fields to appropriate types and validate
            unit = Decimal(unit)
            price = Decimal(price)
            total = Decimal(total)
        except ValueError:
            messages.error(request, 'Unit, price, and total must be numeric.')
            return render(request, 'sale/sale_update.html', {'products': products, 'customers': customers, 'sale': sale})

        try:
            # Ensure the product exists in the inventory
            inventory_item = Inventory.objects.get(product=product)

            # Check if there is enough inventory to make the sale
            if unit > inventory_item.unit:
                messages.error(request, 'Not enough inventory to make this sale.')
                return render(request, 'sale/sale_update.html', {'products': products, 'customers': customers, 'sale': sale})

            # Calculate the quantity based on the unit
            quantity = unit / inventory_item.unit

            # Update Sale instance
            sale.product = product
            sale.customer = customer
            sale.quantity = quantity
            sale.unit = unit
            sale.price = price
            sale.total = total
            sale.created_at = created_at
            sale.save()

            # Update inventory
            inventory_item.unit -= unit - sale.unit  # Adjust inventory based on the new unit value
            inventory_item.save()

            messages.success(request, 'Sale updated successfully.')
            # Redirect to sale list view upon successful update
            return redirect('sale_list')
        except Inventory.DoesNotExist:
            messages.error(request, 'Inventory item for the selected product does not exist.')
            return render(request, 'sale/sale_update.html', {'products': products, 'customers': customers, 'sale': sale})

    # Render the form template for GET requests
    return render(request, 'sale/sale_update.html', {'products': products, 'customers': customers, 'sale': sale})