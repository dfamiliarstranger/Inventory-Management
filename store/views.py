from django.shortcuts import render, redirect, get_object_or_404
from .models import Cap, Color , Preform_type, Supplier, Ticket_Records, Customer, StockItem, update_inventory, Production, Stock, Sales, Notification, Cap_name, Bottle
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout 
from django.contrib import messages
from .forms import CapForm,CustomerForm, SupplierForm, StockItemForm, StockForm
from django.utils import timezone
import datetime
import json
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.db import transaction
from django.db.models import F, Sum, Count
from django.contrib.auth.models import User
from .notification import notify_stock_threshold
from django.http import HttpResponseBadRequest
from datetime import datetime
from django.middleware.csrf import rotate_token
from datetime import datetime
from django.urls import reverse
from decimal import Decimal
from django.db.models.functions import ExtractYear, ExtractMonth
from calendar import monthrange

###############     Create your views here    ###############



def home(request):
    notifications = Notification.objects.order_by('-timestamp').all()
    unread_notifications_count = notifications.filter(is_read=False).count()
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Get month and year from query parameters, or use default values
    selected_month = request.GET.get('month', current_month)
    selected_year = request.GET.get('year', current_year)

    # Filter and annotate stock items by the selected month and year
    preform_stock = (
        Stock.objects.filter(name='Preform', created_at__month=selected_month, created_at__year=selected_year)
        .values('name', 'color', 'preform_type__size', 'preform_type__name', 'product_type')
        .annotate(total_quantity=Sum('quantity'), total_unit=Sum('unit'))
    )

    caps_stock = (
        Stock.objects.filter(name='Cap', created_at__month=selected_month, created_at__year=selected_year)
        .values('name', 'color', 'cap_type__size', 'product_type')
        .annotate(total_quantity=Sum('quantity'), total_unit=Sum('unit'))
    )

    shrinkwrappers_stock = (
        Stock.objects.filter(name='Shrinkwrapper', created_at__month=selected_month, created_at__year=selected_year)
        .values('name', 'color', 'product_type')
        .annotate(total_quantity=Sum('quantity'), total_unit=Sum('unit'))
    )

    bottle_stock = (
        Stock.objects.filter(name='Bottle', created_at__month=selected_month, created_at__year=selected_year)
        .values('name', 'color', 'bottle_type', 'product_type')
        .annotate(total_quantity=Sum('quantity'), total_unit=Sum('unit'))
    )


    total_units_preforms = preform_stock.aggregate(total_units=Sum('total_unit'))['total_units'] or 0
    total_quantity_preforms = preform_stock.aggregate(total_quantity=Sum('total_quantity'))['total_quantity'] or 0

    total_units_caps = caps_stock.aggregate(total_units=Sum('total_unit'))['total_units'] or 0
    total_quantity_caps = caps_stock.aggregate(total_quantity=Sum('total_quantity'))['total_quantity'] or 0

    total_units_shrinkwrappers = shrinkwrappers_stock.aggregate(total_units=Sum('total_unit'))['total_units'] or 0
   
    total_units_bottles = bottle_stock.aggregate(total_units=Sum('total_unit'))['total_units'] or 0

# SALES VIEW
    
    # Filter and aggregate sales by product types
    preform_sales = (
        Sales.objects.filter(product__name='Preform', created_at__month=selected_month, created_at__year=selected_year)
        .values('product__name', 'product__preform_type__name', 'product__preform_type__size', 'product__product_type', 'product__color')
        .annotate(total_quantity=Sum('quantity'), total_price=Sum(F('quantity') * F('price')))
    )

    caps_sales = (
        Sales.objects.filter(product__name='Cap', created_at__month=selected_month, created_at__year=selected_year)
        .values('product__name', 'product__cap_type__size', 'product__product_type', 'product__color')
        .annotate(total_quantity=Sum('quantity'), total_price=Sum(F('quantity') * F('price')))
    )

    shrinkwrappers_sales = (
        Sales.objects.filter(product__name='Shrinkwrapper', created_at__month=selected_month, created_at__year=selected_year)
        .values('product__name', 'product__product_type')
        .annotate(total_quantity=Sum('quantity'), total_price=Sum(F('quantity') * F('price')))
    )

    bottle_sales = (
        Sales.objects.filter(product__name='Bottle', created_at__month=selected_month, created_at__year=selected_year)
        .values('product__name', 'product__bottle_type', 'product__product_type', 'product__color')
        .annotate(total_quantity=Sum('quantity'), total_price=Sum(F('quantity') * F('price')))
    )

    
    total_sales_price = preform_sales.aggregate(total_price=Sum('total_price'))['total_price'] or 0
    total_preforms__quantity = preform_sales.aggregate(total_quantity=Sum('total_quantity'))['total_quantity'] or 0
    caps_sales_price = caps_sales.aggregate(total_price=Sum('total_price'))['total_price'] or 0
    caps_preforms__quantity = caps_sales.aggregate(total_quantity=Sum('total_quantity'))['total_quantity'] or 0
    shrinkwrappers_sales_price = shrinkwrappers_sales.aggregate(total_price=Sum('total_price'))['total_price'] or 0
    shrinkwrappers_preforms__quantity = shrinkwrappers_sales.aggregate(total_quantity=Sum('total_quantity'))['total_quantity'] or 0
    bottle_sales_price = bottle_sales.aggregate(total_price=Sum('total_price'))['total_price'] or 0
    bottle_preforms__quantity = bottle_sales.aggregate(total_quantity=Sum('total_quantity'))['total_quantity'] or 0

# PURCHASES VIEW
    
    # Filter and aggregate sales by product types
    preform_purchases = (
        StockItem.objects.filter(name='Preform', created_at__month=selected_month, created_at__year=selected_year)
        .values('name', 'preform_type__name', 'preform_type__size', 'product_type', 'color__name')
        .annotate(total_quantity=Sum('quantity'), total_price=Sum(F('quantity') * F('price')))
    ) 
    cap_purchases = (
        StockItem.objects.filter(name='Cap', created_at__month=selected_month, created_at__year=selected_year)
        .values('name', 'preform_type__name', 'preform_type__size', 'product_type', 'color__name', 'cap_type__size')
        .annotate(total_quantity=Sum('quantity'), total_price=Sum(F('quantity') * F('price')))
    ) 
    shrinkwrappers_purchases = (
        StockItem.objects.filter(name='Shrinkwrapper', created_at__month=selected_month, created_at__year=selected_year)
        .values('name', 'preform_type__name', 'preform_type__size', 'product_type', 'color__name')
        .annotate(total_quantity=Sum('quantity'), total_price=Sum(F('quantity') * F('price')))
    ) 
    bottle_purchases = (
        StockItem.objects.filter(name='Bottle', created_at__month=selected_month, created_at__year=selected_year)
        .values('name', 'preform_type__name', 'preform_type__size', 'product_type', 'color__name')
        .annotate(total_quantity=Sum('quantity'), total_price=Sum(F('price')))
    ) 
    
    purchase_preforms_quantity = preform_purchases.aggregate(total_quantity=Sum('total_quantity'))['total_quantity'] or 0
    purchase_preforms_price = preform_purchases.aggregate(total_price=Sum('total_price'))['total_price'] or 0
    purchase_caps_quantity = cap_purchases.aggregate(total_quantity=Sum('total_quantity'))['total_quantity'] or 0
    purchase_caps_price = cap_purchases.aggregate(total_price=Sum('total_price'))['total_price'] or 0
    purchase_shrinkwrappers_quantity = shrinkwrappers_purchases.aggregate(total_quantity=Sum('total_quantity'))['total_quantity'] or 0
    purchase_shrinkwrappers_price = shrinkwrappers_purchases.aggregate(total_price=Sum('total_price'))['total_price'] or 0



    context = {
        'purchase_shrinkwrappers_quantity':purchase_shrinkwrappers_quantity,
        'purchase_shrinkwrappers_price':purchase_shrinkwrappers_price,
        'cap_purchases':cap_purchases,
        'preform_purchases':preform_purchases,
        'bottle_purchases': bottle_purchases,
        'shrinkwrappers_purchases':shrinkwrappers_purchases,
        'purchase_caps_price':purchase_caps_price,
        'purchase_caps_quantity':purchase_caps_quantity,
        'purchase_preforms_price':purchase_preforms_price,
        'purchase_preforms_quantity':purchase_preforms_quantity,
        'bottle_preforms__quantity':bottle_preforms__quantity,
        'bottle_sales_price':bottle_sales_price,
        'shrinkwrappers_preforms__quantity':shrinkwrappers_preforms__quantity,
        'shrinkwrappers_sales_price':shrinkwrappers_sales_price,
        'caps_preforms__quantity':caps_preforms__quantity,
        'caps_sales_price':caps_sales_price,
        'total_sales_price':total_sales_price,
        'total_preforms__quantity':total_preforms__quantity,
        'preform_sales': preform_sales,
        'caps_sales': caps_sales,
        'shrinkwrappers_sales': shrinkwrappers_sales,
        'bottle_sales': bottle_sales,
        'total_units_preforms':total_units_preforms,
        'total_quantity_preforms':total_quantity_preforms,
        'total_units_caps':total_units_caps,
        'total_quantity_caps':total_quantity_caps,
        'total_units_shrinkwrappers':total_units_shrinkwrappers,
        'total_units_bottles':total_units_bottles,
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
        'preform_stock': preform_stock,
        'caps_stock': caps_stock,
        'shrinkwrappers_stock': shrinkwrappers_stock,
        'bottle_stock': bottle_stock,
        'selected_month': int(selected_month),
        'selected_year': int(selected_year),
        'months': range(1, 13),
        'years': range(2020, current_year + 1),
    }
    
    return render(request, 'base/home.html', context)

def csrf_failure_view(request, reason=""):
    # You can customize this view to render a custom template or redirect users
    return render(request, 'base/login.html', {'reason': reason})


def error_page(request):
    return render(request, 'base/test.html', {'user': request.user})

def user_login(request):
    if request.method == 'POST':
        # Rotate CSRF token
        rotate_token(request)
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'base/login.html', {'error_message': 'Invalid username or password'})
    else:
        # Render login form
        return render(request, 'base/login.html')


def user_logout(request):
    logout(request)
    return redirect('user_login')

            ###############     Create Product Views    ###############

@login_required
def cap(request):
    cap = Cap.objects.all()
    return render(request, ('products/cap/index.html'), {'caps':cap})


@login_required
def delete_cap(request, pk):
    # Retrieve the Cap_name object to be deleted
    cap = get_object_or_404(Cap, id=pk)
    
    if request.method == 'POST':
        # Delete the Cap_name object
        cap.delete()
        # Redirect to the cap_name list page
        return redirect('product')
    
    # Optionally, render a confirmation page
    return render(request, 'settings/delete_cap.html', {'cap': cap})

@login_required
def create_cap(request):
    if request.method == "POST":
        form = CapForm(request.POST)
        if form.is_valid():
           form.save()
           return redirect('cap')
        else:
            return redirect('create_cap')
    else:
        form = CapForm()
    return render(request, 'products/cap/form.html', {'form':form})


@login_required
def preform_type(request):
    preform_type = Preform_type.objects.all()
    return render(request, ('products/cap/index.html'), {'preform_types':preform_type})


@login_required
def delete_preform_type(request, pk):
    # Retrieve the Cap_name object to be deleted
    preform_type = get_object_or_404(Preform_type, id=pk)
    
    if request.method == 'POST':
        # Delete the Cap_name object
        preform_type.delete()
        # Redirect to the cap_name list page
        return redirect('product')
    
    # Optionally, render a confirmation page
    return render(request, 'settings/delete_preform_type.html', {'preform_type': preform_type})

            ############       Create Clients Views         ############   
@login_required
def supplier(request):
    supplier = Supplier.objects.all()
    return render(request, 'clients/supplier/index.html', {'suppliers':supplier})



@login_required
def update_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated successfully.')
            return redirect('supplier')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'clients/supplier/update_supplier.html', {'form': form, 'supplier': supplier})

@login_required
def delete_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Supplier deleted successfully.')
        return redirect('supplier')
    return render(request, 'clients/supplier/delete_supplier.html', {'supplier': supplier})

@login_required
def create_supplier(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
           form.save()
           return redirect('supplier')
        else:
            return redirect('create_supplier')
    else:
        form = SupplierForm()
    return render(request, 'clients/supplier/form.html', {'form':form})


@login_required
def customer(request):
    customer = Customer.objects.all()
    notifications = Notification.objects.all()
    unread_notifications_count = notifications.filter(is_read=False).count()
    return render(request, 'clients/customer/index.html', {'customers':customer,'unread_notifications_count':unread_notifications_count})

@login_required
def create_customer(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
           form.save()
           return redirect('customer')
        else:
            return redirect('create_customer')
    else:
        form = CustomerForm()
    return render(request, 'clients/customer/form.html', {'form':form})

@login_required
def update_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully.')
            return redirect('customer')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'clients/customer/update_customer.html', {'form': form, 'customer': customer})

@login_required
def delete_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully.')
        return redirect('customer')
    return render(request, 'clients/customer/delete_customer.html', {'customer': customer})


                    ################    Stock Item    #######################
@login_required
def add_stock_item(request):
    stock_form = StockItemForm()
    preform_type = Preform_type.objects.all()
    cap = Cap.objects.all()
    supplier = Supplier.objects.all()
    cap_name = Cap_name.objects.all()
    
    if request.method == 'POST':
        form = StockItemForm(request.POST)
        if form.is_valid():
            # Extracting data from the form
            created_at = request.POST.get('created_at', '') 
            name = request.POST.get('name', '') 
            color = request.POST.get('color', '')  
            quantity = request.POST.get('quantity', '')  
            supplier_id = request.POST.get('supplier', '')  
            cap_type_id = request.POST.get('cap_type', '')  
            preform_type_id = request.POST.get('preform_type', '')  
            product_type = request.POST.get('product_type', '')  
            price = request.POST.get('price', '')  
            total = request.POST.get('total', '') 
             
            
            # Validation
            if not (name and total and quantity and supplier_id and price):
                return HttpResponse("All fields are required.")

            try:
                supplier = Supplier.objects.get(id=supplier_id)
            except Supplier.DoesNotExist:
                return HttpResponse("Invalid Supplier selected.")
            
            # Creating a new stock item
            stock_item = form.save(commit=False)
            stock_item.supplier = supplier
               
            # Calculating total price
            total = float(quantity) * float(price)
            stock_item.total = total
            
            # Saving the stock item
            stock_item.save()
            
            # Update inventory
            update_inventory(stock_item)
            messages.success(request, 'Stock added successfully.')
            return redirect('stock') 
        else:
            print(form.errors)
            return redirect('add_stock')
    else:
        color = Color.objects.all()
        return render(request, 'store/add_stock/index.html', {'stock_form': stock_form, 'preform_types': preform_type, 'caps': cap, 'suppliers': supplier, 'color':color, 'cap_name':cap_name})

@login_required
def update_stock_item(request, pk):
    stock_item = get_object_or_404(Stock, pk=pk)
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock_item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stock item updated successfully.')
            return redirect('stock_list')
    else:
        form = StockItemForm(instance=stock_item)
    return render(request, 'stock/update_stock.html', {'form': form, 'stock_item': stock_item})

@login_required
def delete_stock_item(request, pk):
    stock_item = get_object_or_404(Stock, pk=pk)
    if request.method == 'POST':
        stock_item.delete()
        messages.success(request, 'Stock item deleted successfully.')
        return redirect('stock_list')
    return render(request, 'stock/delete_stock.html', {'stock_item': stock_item})


@login_required
def purchase_history(request):
    stock = StockItem.objects.order_by('-created_at')  # Order by the 'created_at' field in descending order
    paginator = Paginator(stock, 10)  # Show 10 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'store/add_stock/details.html', {'stock': stock,'page_obj':page_obj})

threshold_values = {
            'Cap': 5000,
            'Preform': 5000,
            'Bottle': 3000,
            'Shrinkwrapper': 30,  # Define a threshold value for "Shrinkwrapper"
            }

@login_required
def stock_detail(request):
    # Get all stock items
     
    updated_stock_items = Stock.objects.order_by('-created_at')

    # Iterate through each stock item
    for updated_stock_item in updated_stock_items:
        # If the stock quantity is zero, delete the stock record
        if updated_stock_item.unit == 0:
            updated_stock_item.delete()
        # # Trigger notification if the stock quantity is below the threshold
       
        # notify_stock_threshold(request.user, updated_stock_item)
        
        elif updated_stock_item.unit <= threshold_values.get(updated_stock_item.name, 5000) and not updated_stock_item.notification_sent:
            
            # Notify user if stock threshold is met and a notification has not been sent
            notify_stock_threshold(request.user, updated_stock_item)
            
            # Set notification_sent to True
            updated_stock_item.notification_sent = True  
            updated_stock_item.save()

    paginator = Paginator(updated_stock_items, 10)  # Show 10 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Retrieve the updated stock items after deletion
    stock_items = Stock.objects.all().order_by('-id')
    notifications = Notification.objects.all()
    unread_notifications_count = notifications.filter(is_read=False).count()

    # Get the count of stock items
    stock_count = stock_items.count()

    return render(request, 'stock/index.html', {'stock_item': stock_items, 'page_obj':page_obj, 'stock_count': stock_count, 'unread_notifications_count':unread_notifications_count})



#####################                     PRODUCTION                          ######################

@login_required
def production(request):
    if request.method == 'POST':
        # Get form data
        created_at = request.POST.get('created_at')
        product_id = request.POST.get('product')
        quantity = request.POST.get('quantity')
        damages = request.POST.get('damages')
        waste_bottle = request.POST.get('waste_bottle')
        good_bottle = request.POST.get('good_bottle')
        bottle_size = request.POST.get('bottle_size')
        bottle_color_id = request.POST.get('color')
        bottle_unit = request.POST.get('bottle_unit')
        
        try:
            bottle_color = Color.objects.get(pk=bottle_color_id)
        except Color.DoesNotExist:
            messages.error(request, 'Invalid color selection.')
            return redirect('production')

        # Perform input validation
        if not product_id or not quantity or not bottle_color or not good_bottle:
            messages.error(request, 'Please fill all required fields.')
            return redirect('production')
        
        # Check if quantity equals damages + good bottle + bad bottle
        if int(quantity) != int(damages) + int(good_bottle) + int(waste_bottle):
            messages.error(request, 'Quantity should be equal to damages + good bottles + bad bottles.')
            return redirect('production')

        # Perform business logic checks
        try:
            quantity = int(quantity)
            waste_bottle = int(waste_bottle)
            good_bottle = int(good_bottle)
            bottle_size = int(bottle_size)
        except ValueError:
            messages.error(request, 'Quantity fields must be integers.')
            return redirect('production')

        product = Stock.objects.get(pk=product_id)

        # Check if there's enough preform quantity
        if int(product.unit) < quantity:
            messages.error(request, 'Insufficient stock quantity.')
            return redirect('production')
        try:
            # Start a database transaction
            with transaction.atomic():
                # Deduct product quantity used from stock
                product.unit -= quantity
                product.save()

                # Create Production object
                production_instance = Production.objects.create(
                    created_at=created_at,
                    product=product,
                    product_quantity=quantity,
                    damages=damages,
                    waste_bottle=waste_bottle,
                    good_bottle=good_bottle,
                    bottle_size=bottle_size,
                    bottle_color=bottle_color,
                    bottle_unit=bottle_unit
                )

                # Create or update Bottle record
                bottle, created = Bottle.objects.get_or_create(
                    bottle_unit=bottle_unit,
                    bottle_size=bottle_size,
                    bottle_color=bottle_color,
                    defaults={'quantity': good_bottle, 'created_at': created_at}
                )

                 # Create or increment Bottle Stock
                bottle_stock, created = Stock.objects.get_or_create(
                    name='Bottle',
                    color=bottle_color,
                    bottle_type=bottle_size,
                    product_type=bottle_unit,
                    defaults={'unit': good_bottle}  # Set default unit if creating new
                )
                if not created:
                    # Increment the quantity if the stock already exists
                    Stock.objects.filter(pk=bottle_stock.pk).update(unit=F('unit') + good_bottle)

                messages.success(request, 'Production record created successfully.')
                return redirect('record')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('production')

    else:
        stock = Stock.objects.all()
        color = Color.objects.all()
        return render(request, 'production/index.html', {'stock': stock, 'color':color})
    


@login_required
def production_record(request):
    production_records = Production.objects.order_by('-created_at')
    paginator = Paginator(production_records, 5)  # Show 10 records per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    notifications = Notification.objects.all()
    unread_notifications_count = notifications.filter(is_read=False).count()

    return render(request, 'production/summary.html', {
        'page_obj': page_obj,
        'unread_notifications_count': unread_notifications_count
    })



@login_required
def sales_record(request):
    sales = Sales.objects.all()
    paginator = Paginator(sales, 10)  # Show 10 records per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    notifications = Notification.objects.all()
    unread_notifications_count = notifications.filter(is_read=False).count()
    return render(request, 'sales/index.html', {'sales': sales, 'page_obj': page_obj, 'unread_notifications_count':unread_notifications_count})


@login_required
def sales_form(request):
    if request.method == 'POST':
        # Get form data
        created_at = request.POST.get('created_at')
        product_id = request.POST.get('product_id')
        customer_id = request.POST.get('customer_id')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')

        # Perform input validation
        if not product_id or not customer_id or not quantity or not price or not created_at:
            messages.error(request, 'Please fill all fields.')
            return redirect('sales_form')

        # Perform business logic checks
        try:
            quantity = int(quantity)
            price = int(price)
        except ValueError:
            messages.error(request, 'Quantity and price must be integers.')
            return redirect('sales_form')

        product = Stock.objects.get(pk=product_id)

           
        if product.unit < quantity:
                messages.error(request, 'Insufficient stock quantity.')
                return redirect('sales_form')
        
        # Adjust quantity based on product type
        
        
        try:
            # Start a database transaction
            with transaction.atomic():
                # Deduct product quantity used from stock
                product.unit -= quantity
                if product.name.lower() == 'preform':
                    preform_type = product.preform_type
                    adjusted_quantity = quantity / preform_type.quantity_per_bag
                    product.quantity = adjusted_quantity
                elif product.name.lower() == 'cap':
                    cap_type = product.cap_type
                    adjusted_quantity = quantity / cap_type.quantity_per_bag
                    product.quantity = adjusted_quantity
                else:
                    product.quantity -= quantity

                product.save()

               
                # Calculate total, create Sales object, and handle success
                total = quantity * price
                sale = Sales.objects.create(
                    created_at=created_at,
                    product=product,
                    customer_id=customer_id,
                    quantity=quantity,
                    price=price,
                    total=total
                )
                
                messages.success(request, 'Sale completed successfully.')
                return redirect('sales_record')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('sales_form')

    else:
        # Fetch required data for rendering form
        stock = Stock.objects.all()
        customer = Customer.objects.all()
        sales = Sales.objects.all()
        color = Color.objects.all()
        
        # Check for None value in product.unit before rendering the form
        products_with_unspecified_quantity = [item for item in stock if item.unit is None]
        

        return render(request, 'sales/forms.html', {'sales': sales, 'stock': stock, 'customer': customer, 'color': color})



@login_required
def show_notification(request):
    # Fetch notifications and pass them to the template
    notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')
    unread_notifications_count = notifications.filter(is_read=False).count()
    return render(request, 'notification/index.html', {'notifications': notifications, 'unread_notifications_count': unread_notifications_count})


@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id)
    notification.delete()
    return redirect('notify')

@login_required
def clear_notifications(request):
    if request.method == 'GET':
        # Mark all notifications as read for the current user
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        # Redirect back to the notifications page
        return redirect('notify')

@login_required    
def invoice(request):
    error = None
    sales_data = None
    customers = Customer.objects.all()
    notifications = Notification.objects.all()
    unread_notifications_count = notifications.filter(is_read=False).count()

    if request.method == 'GET':
        customer_str = request.GET.get('customer')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        if customer_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
                
                sales_data = Sales.objects.filter(customer__name=customer_str)
                
                if start_date:
                    sales_data = sales_data.filter(created_at__gte=start_date)
                if end_date:
                    sales_data = sales_data.filter(created_at__lte=end_date)
                
                if not sales_data:
                    error = 'No sales found for the selected criteria.'
            except ValueError:
                error = 'Invalid date format. Please use YYYY-MM-DD.'

    return render(request, 'invoice/base.html', {'sales_data': sales_data, 'customers': customers, 'error': error,'unread_notifications_count':unread_notifications_count})

@login_required  
def print_invoice(request):
    if request.method == 'GET':
        selected_sales_ids = request.GET.getlist('selected_sales')  # Get selected sales IDs from the query parameters
        sales_data = Sales.objects.filter(id__in=selected_sales_ids) 
        
         # Calculate the sum total
        sum_total = sum(sale.total for sale in sales_data) 
        # Filter sales data based on selected IDs
        return render(request, 'invoice/index.html', {'sales_data': sales_data, 'sum_total': sum_total})

    else:
        # Handle POST request if needed
        pass

@login_required
def settings(request):
    notifications = Notification.objects.all()
    unread_notifications_count = notifications.filter(is_read=False).count()
    return render(request, 'settings/index.html',{'unread_notifications_count':unread_notifications_count})





@login_required
def products(request):
    if request.method == 'POST':
        # Check if the form is for adding a new Preform type
        if 'add_preform' in request.POST:
            preform_name = request.POST.get('preform_name')
            preform_size = request.POST.get('preform_size')
            preform_quantity_per_bag = request.POST.get('preform_quantity_per_bag')
            if preform_name and preform_size and preform_quantity_per_bag:
                Preform_type.objects.create(
                    name=preform_name,
                    size=preform_size,
                    quantity_per_bag=preform_quantity_per_bag
                )
                messages.success(request, 'Preform added successfully.')
            else:
                messages.error(request, 'Please fill in all the fields.')

        # Check if the form is for adding a new Cap type
        elif 'add_cap' in request.POST:
            
            cap_size = request.POST.get('cap_size')
            cap_quantity_per_bag = request.POST.get('cap_quantity_per_bag')
            if  cap_size and cap_quantity_per_bag:
                Cap.objects.create(
                
                    size=cap_size,
                    quantity_per_bag=cap_quantity_per_bag
                )
                messages.success(request, 'Cap added successfully.')
            else:
                messages.error(request, 'Please fill in all the fields.')

        # Check if the form is for adding a new Cap type name
        elif 'add_cap_type' in request.POST:
            cap_type_name = request.POST.get('cap_type_name')
            if cap_type_name:
                Cap_name.objects.create(name=cap_type_name)
                messages.success(request, 'Cap type added successfully.')
            else:
                messages.error(request, 'Please provide a name.')

        return redirect('product')

    preform_type = Preform_type.objects.all()
    cap = Cap.objects.all()
    cap_name = Cap_name.objects.all()

    return render(request, 'settings/product.html', {
        'preform_type': preform_type,
        'cap': cap,
        'cap_name': cap_name,
    })

@login_required
def color(request):
    if request.method == 'POST':
        # Get the color name from the form data
        color_name = request.POST.get('name')

        # Check if the color name is not empty
        if color_name:
            # Create a new Color object and save it to the database
            Color.objects.create(name=color_name)
            # Redirect to the same page after adding color
            return redirect('color')

    # Retrieve all colors from the database
    color = Color.objects.all()
    
    # Render the template with the list of colors
    return render(request, 'color/index.html', {'color': color})


@login_required
# View for rendering the form
def ticket_form(request):
    stocks = Stock.objects.all()
    return render(request, 'settings/ticket.html', {'stocks': stocks})

@login_required
def ticket_update(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    
    if request.method == 'POST':
        # Get form data
        stock_id = request.POST.get('stock_id')
        option = request.POST.get('option')
        quantity = int(request.POST.get('quantity'))
        
        # Check if the stock is sufficient for deduction
        if option == 'shortage' and stock.unit < quantity:
            messages.error(request, 'Insufficient stock for deduction')
            return redirect('ticket_form')
        
        # Update stock unit based on selected option
        if option == 'excess':
            stock.unit += quantity
        elif option == 'shortage':
            stock.unit -= quantity
        
        # Save the updated stock
        stock.save()
        
        # Determine product type for the record
        product_type = None
        if stock.preform_type:
            product_type = stock.preform_type
        elif stock.cap_type:
            product_type = stock.cap_type
        elif stock.product_type:
            product_type = stock.product_type
        elif stock.bottle_type:
            product_type = stock.bottle_type
        
        # Create a record for the stock update
        record = Ticket_Records.objects.create(
            product=stock,
            product_type=product_type,
            action=option,
            quantity=quantity,
          # Use timezone.now() for the current datetime
        )
        
        # Redirect to the stock detail page or any other appropriate page
        return redirect('ticket_update', stock_id=stock.id)
   
    return redirect('stock_list')

@login_required
def search_view(request):
    if request.method == 'GET':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        option = request.GET.get('option')

        # Validate start_date and end_date
        if start_date is None or end_date is None:
            # Handle the case when start_date or end_date is not provided
            return render(request, 'settings/reports.html', {'error_message': 'Please provide both start date and end date'})

        # Extract only the date part from the start date parameter
        start_date = datetime.strptime(start_date.split()[0], '%Y-%m-%d')
        end_date = datetime.strptime(end_date.split()[0], '%Y-%m-%d')

        # Initialize queryset
        queryset = None

        # Filter data based on the selected option
        if option == 'sales':
            # Redirect to sales_report view
            url = reverse('sales_report') + f'?queryset=sales&start_date={start_date}&end_date={end_date}'
            return redirect(url)
        elif option == 'purchases':
            # Redirect to purchases_report view
            url = reverse('purchase_report') + f'?queryset=purchases&start_date={start_date}&end_date={end_date}'
            return redirect(url)
        elif option == 'tickets':
            # Redirect to tickets_report view
            url = reverse('ticket_report') + f'?queryset=production&start_date={start_date}&end_date={end_date}'
            return redirect(url)
        elif option == 'production':
            # Redirect to production_report view with queryset as query parameter
            url = reverse('production_report') + f'?queryset=production&start_date={start_date}&end_date={end_date}'
            return redirect(url)
        else:
            # Handle invalid option
            return render(request, 'settings/reports.html', {'error_message': 'Invalid option selected'})

    else:
        return render(request, 'settings/reports.html')

  
@login_required
def production_report(request):
    if request.method == 'GET':
        # Retrieve parameters from the URL
        queryset = request.GET.get('queryset')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        # Remove time part from the date strings
        start_date_str = start_date_str.split()[0]
        end_date_str = end_date_str.split()[0]

        # Convert start_date and end_date strings to datetime objects
        start_date = timezone.make_aware(datetime.strptime(start_date_str, '%Y-%m-%d'))
        end_date = timezone.make_aware(datetime.strptime(end_date_str, '%Y-%m-%d'))

        # Retrieve production records based on the specified date range
        production_records = Production.objects.filter(created_at__range=[start_date, end_date])

        # Calculate totals for each production summary item
        total_good_bottles = production_records.aggregate(Sum('good_bottle'))['good_bottle__sum']  
        total_preforms_used = production_records.aggregate(Sum('product_quantity'))['product_quantity__sum']
        total_damaged_preforms = production_records.aggregate(Sum('damages'))['damages__sum']
        total_waste_bottles = production_records.aggregate(Sum('waste_bottle'))['waste_bottle__sum']

        # Render the production report template with the retrieved data
        return render(request, 'settings/production_report.html', {'queryset': queryset, 'start_date': start_date, 'end_date': end_date, 'production_records': production_records, 'total_good_bottles': total_good_bottles, 'total_preforms_used': total_preforms_used, 'total_damaged_preforms': total_damaged_preforms,'total_waste_bottles': total_waste_bottles,})


@login_required
def sales_report(request):
    if request.method == 'GET':
        # Retrieve parameters from the URL
        queryset = request.GET.get('queryset')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        # Remove time part from the date strings
        start_date_str = start_date_str.split()[0]
        end_date_str = end_date_str.split()[0]

        # Convert start_date and end_date strings to datetime objects
        start_date = timezone.make_aware(datetime.strptime(start_date_str, '%Y-%m-%d'))
        end_date = timezone.make_aware(datetime.strptime(end_date_str, '%Y-%m-%d'))

        # Retrieve production records based on the specified date range
        sales_records = Sales.objects.filter(created_at__range=[start_date, end_date])

        # Initialize variables to hold aggregate values
        bottles_sold = Decimal(0)
        preforms_sold = Decimal(0)
        shrinkwrappers_sold = Decimal(0)
        caps_sold = Decimal(0)
        bottles_total = Decimal(0)
        preforms_total = Decimal(0)
        shrinkwrappers_total = Decimal(0)
        caps_total = Decimal(0)

        # Calculate total quantities sold for each product type
        bottles_sold = sales_records.filter(product__name='Bottle').aggregate(total_sold=Sum('quantity'))['total_sold'] or Decimal(0)
        preforms_sold = sales_records.filter(product__name='Preform').aggregate(total_sold=Sum('quantity'))['total_sold'] or Decimal(0)
        shrinkwrappers_sold = sales_records.filter(product__name='Shrinkwrapper').aggregate(total_sold=Sum('quantity'))['total_sold'] or Decimal(0)
        caps_sold = sales_records.filter(product__name='Cap').aggregate(total_sold=Sum('quantity'))['total_sold'] or Decimal(0)

        # Calculate the sum of all totals
        total_quantity_sold = bottles_sold + preforms_sold + shrinkwrappers_sold + caps_sold

        # Calculate total quantities sold for each product type
        bottles_total = sales_records.filter(product__name='Bottle').aggregate(total_sold=Sum('total'))['total_sold'] or Decimal(0)
        preforms_total = sales_records.filter(product__name='Preform').aggregate(total_sold=Sum('total'))['total_sold'] or Decimal(0)
        shrinkwrappers_total = sales_records.filter(product__name='Shrinkwrapper').aggregate(total_sold=Sum('total'))['total_sold'] or Decimal(0)
        caps_total = sales_records.filter(product__name='Cap').aggregate(total_sold=Sum('total'))['total_sold'] or Decimal(0)

        # Calculate the sum of all totals
        total_stk = bottles_total + preforms_total + shrinkwrappers_total + caps_total

        # Render the production report template with the retrieved data
        return render(request, 'settings/sale_report.html', {
            'queryset': queryset,
            'start_date': start_date,
            'end_date': end_date,
            'sales_records': sales_records,
            'caps_total': caps_total,
            'preforms_total': preforms_total,
            'bottles_total': bottles_total,
            'shrinkwrappers_total': shrinkwrappers_total,
            'total_stk': total_stk,
            'bottles_sold': bottles_sold,
            'preforms_sold': preforms_sold,
            'shrinkwrappers_sold': shrinkwrappers_sold,
            'caps_sold': caps_sold,
            'total_quantity_sold': total_quantity_sold
        })
    

@login_required
def purchase_report(request):
    if request.method == 'GET':
        # Retrieve parameters from the URL
        queryset = request.GET.get('queryset')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        # Remove time part from the date strings
        start_date_str = start_date_str.split()[0]
        end_date_str = end_date_str.split()[0]

        # Convert start_date and end_date strings to datetime objects
        start_date = timezone.make_aware(datetime.strptime(start_date_str, '%Y-%m-%d'))
        end_date = timezone.make_aware(datetime.strptime(end_date_str, '%Y-%m-%d'))

        # Retrieve production records based on the specified date range
        purchase_records = StockItem.objects.filter(created_at__range=[start_date, end_date])

         # Filter records for products 'preform', 'cap', and 'shrinkwrapper'
        preform_records = purchase_records.filter(name='Preform')
        cap_records = purchase_records.filter(name='Cap')
        shrinkwrapper_records = purchase_records.filter(name='Shrinkwrapper')

        # Calculate totals for each product category
        total_preform = preform_records.aggregate(Sum('total'))['total__sum'] or 0
        total_cap = cap_records.aggregate(Sum('total'))['total__sum'] or 0
        total_shrinkwrapper = shrinkwrapper_records.aggregate(Sum('total'))['total__sum'] or 0

        # Calculate totals for each production summary item
        total = purchase_records.aggregate(Sum('total'))['total__sum']  
        

        # Render the production report template with the retrieved data
        return render(request, 'settings/purchase_report.html', {
            'queryset': queryset,
            'start_date': start_date,
            'end_date': end_date,
            'total_preform':total_preform,
            'total_cap':total_cap,
            'total_shrinkwrapper':total_shrinkwrapper,
            'purchase_records': purchase_records,
            'total':total
        })

@login_required
def ticket_report(request):
    if request.method == 'GET':
        # Retrieve parameters from the URL
        queryset = request.GET.get('queryset')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        # Remove time part from the date strings
        start_date_str = start_date_str.split()[0]
        end_date_str = end_date_str.split()[0]

        # Convert start_date and end_date strings to datetime objects
        start_date = timezone.make_aware(datetime.strptime(start_date_str, '%Y-%m-%d'))
        end_date = timezone.make_aware(datetime.strptime(end_date_str, '%Y-%m-%d'))

        # Retrieve production records based on the specified date range
        ticket_records = Ticket_Records.objects.filter(created_at__range=[start_date, end_date])

        # Render the production report template with the retrieved data
        return render(request, 'settings/ticket_report.html', {
            'queryset': queryset,
            'start_date': start_date,
            'end_date': end_date,
            'ticket_records': ticket_records,
            
        })


def add_bottle(request):
    if request.method == 'POST':
        # Get form data
        
        created_at = request.POST.get('created_at')
        name = request.POST.get('name', '')
        bottle_color = request.POST.get('color', '')
        good_bottle = request.POST.get('quantity', '')  
        bottle_unit = request.POST.get('product_type', '') 
        bottle_size = request.POST.get('bottle_size')

        # Perform input validation for required fields
        if not bottle_color or not bottle_size or not good_bottle:
            messages.error(request, 'Please fill all required fields.')
            return redirect('add_bottle')

        try:
            bottle_color = Color.objects.get(pk=bottle_color)
        except Color.DoesNotExist:
            messages.error(request, 'Invalid color selection.')
            return redirect('add_bottle')

        try:
            quantity = int(good_bottle)
            bottle_size = int(bottle_size)
            
        except ValueError:
            messages.error(request, 'Quantity, bottle size, must be integers.')
            return redirect('add_bottle')

        # Optional fields handling
        

        try:
            # Start a database transaction
            with transaction.atomic():
                # Create or increment Bottle Stock
                bottle_stock, created = Stock.objects.get_or_create(
                    name='Bottle',
                    color=bottle_color,
                    bottle_type=bottle_size,
                    product_type=bottle_unit,
                    quantity=good_bottle,
                    unit=good_bottle,
                    defaults={'created_at': created_at, }  # Set default unit if creating new
                )
                if not created:
                    # Increment the quantity if the stock already exists
                    Stock.objects.filter(pk=bottle_stock.pk).update(unit=quantity + quantity)

                # Create StockItem entry
                stock_item = StockItem.objects.create(
                    name='Bottle',
                    price=bottle_size,
                    quantity=str(quantity),
                    created_at=created_at,
                
                    color=bottle_color,
                    product_type=bottle_unit,
                   
                    unit=quantity
                )

                # Update inventory
                update_inventory(stock_item)

                messages.success(request, 'Bottle stock updated successfully.')
                return redirect('stock')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('add_stock')

    else:
        color = Color.objects.all()
        
        return render(request, 'store/add_stock/index.html', {
            'color': color,
           
        })
    

@login_required
def remove_stock_item(request, item_id):
    # Get the stock item to be removed
    stock_item = get_object_or_404(StockItem, id=item_id)
    preform_type = Preform_type.objects.all()
    cap = Cap.objects.all()
    supplier = Supplier.objects.all()
    
    if request.method == 'POST':
        # Remove the stock item
        try:
            remove_from_inventory(stock_item)
            stock_item.delete()
            messages.success(request, 'Stock removed successfully.')
            return redirect('stock')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('remove_stock', item_id=item_id)
    else:
        color = Color.objects.all()
        stock_form = StockItemForm(instance=stock_item)
        return render(request, 'settings/reverse_prompt.html', {'stock_form': stock_form, 'preform_types': preform_type, 'caps': cap, 'suppliers': supplier, 'color': color, 'stock_item': stock_item})

def remove_from_inventory(stock_item):
    try:
        with transaction.atomic():
            inventory_item = Stock.objects.filter(
                name=stock_item.name,
                color=stock_item.color,
                product_type=stock_item.product_type,
                cap_type=stock_item.cap_type,
                preform_type=stock_item.preform_type,
            ).first()

            if inventory_item:
                # Update quantity and unit
                inventory_item.quantity = Decimal(inventory_item.quantity) - Decimal(stock_item.quantity)
                inventory_item.unit = Decimal(inventory_item.unit) - Decimal(stock_item.unit)
                
                if inventory_item.unit < 0:
                    raise ValueError("Insufficient stock item")
                elif inventory_item.unit == 0:
                    inventory_item.delete()
                else:
                    inventory_item.save()
            else:
                raise ValueError("Inventory item does not exist.")
    except Exception as e:
        # Handle exceptions
        print(f"An error occurred: {e}")
        raise


@login_required
def reverse_sale(request, sale_id):
    # Get the sale to be reversed
    sale = get_object_or_404(Sales, id=sale_id)
    stock_item = sale.product

    if request.method == 'POST':
        # Reverse the sale
        try:
            reverse_sale_transaction(sale, stock_item)
            sale.delete()
            messages.success(request, 'Sale reversed successfully.')
            return redirect('sales_record')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('reverse_sale', sale_id=sale_id)
    else:
        stock_form = StockItemForm(instance=stock_item)
        return render(request, 'settings/reverse_sales.html', {'sale': sale, 'stock_form': stock_form, 'stock_item': stock_item})

def reverse_sale_transaction(sale, stock_item):
    try:
        with transaction.atomic():
            # Update inventory to reflect reversal
            stock_item.unit = Decimal(stock_item.unit) + Decimal(sale.quantity)
            stock_item.save()
    except Exception as e:
        # Handle exceptions
        print(f"An error occurred: {e}")
        raise



@login_required
def reverse_production(request, production_id):
    try:
        production_instance = Production.objects.get(pk=production_id)
    except Production.DoesNotExist:
        messages.error(request, 'Production record not found.')
        return redirect('record')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Revert the stock deduction
                product = production_instance.product
                product.unit += production_instance.product_quantity
                product.save()

                # Revert the bottle stock increment
                try:
                    bottle_stock = Stock.objects.get(
                        name='Bottle',
                        color=production_instance.bottle_color,
                        bottle_type=production_instance.bottle_size,
                        product_type=production_instance.bottle_unit
                    )
                except Stock.DoesNotExist:
                    messages.error(request, 'Corresponding bottle stock not found.')
                    return redirect('record')

                bottle_stock.unit -= production_instance.good_bottle
                if bottle_stock.unit < 0:
                    messages.error(request, 'Bottle stock cannot be negative.')
                    return redirect('record')
                bottle_stock.save()

                # Delete the production record
                production_instance.delete()

                messages.success(request, 'Production record reversed successfully.')
                return redirect('record')

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('record')

    else:
        return render(request, 'settings/reverse_production.html', {'production': production_instance})
    

@login_required
def cap_name(request):
    if request.method == 'POST':
        # Get the color name from the form data
        cap_name = request.POST.get('name')

        # Check if the color name is not empty
        if cap_name:
            # Create a new Color object and save it to the database
            Color.objects.create(name=cap_name)
            # Redirect to the same page after adding color
            return redirect('cap_name')

    # Retrieve all colors from the database
    cap_name = Cap_name.objects.all()
    
    # Render the template with the list of colors
    return render(request, 'color/index.html', {'cap_name': cap_name})


@login_required
def delete_cap_name(request, pk):
    # Retrieve the Cap_name object to be deleted
    cap_name = get_object_or_404(Cap_name, id=pk)
    
    if request.method == 'POST':
        # Delete the Cap_name object
        cap_name.delete()
        # Redirect to the cap_name list page
        return redirect('product')
    
    # Optionally, render a confirmation page
    return render(request, 'settings/delete_cap_name.html', {'cap_name': cap_name})
       