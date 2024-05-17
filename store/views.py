from django.shortcuts import render, redirect, get_object_or_404
from .models import Cap, Color , Preform_type, Supplier, Ticket_Records, Customer, StockItem, update_inventory, Production, Stock, Sales, Notification
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout 
from django.contrib import messages
from .forms import CapForm,CustomerForm, SupplierForm, StockItemForm
from django.utils import timezone
import datetime
from django.http import HttpResponse
from django.db import transaction
from django.db.models import F, Sum
from django.contrib.auth.models import User
from .notification import notify_stock_threshold
from django.http import HttpResponseBadRequest
from datetime import datetime
from django.middleware.csrf import rotate_token
from datetime import datetime
from django.urls import reverse
from decimal import Decimal

###############     Create your views here    ###############

@login_required
def home(request):
    notifications = Notification.objects.order_by('-timestamp').all()
    stock_items = Stock.objects.all().order_by('-id')
    stock_count = stock_items.count()
    unread_notifications_count = notifications.filter(is_read=False).count()
    # Query for the total sum of all sales amounts
    total_sales_amount = Sales.objects.count()
    total_purchase_amount = StockItem.objects.count()
    return render(request, ('base/home.html'), {'notifications': notifications, 'stock_item': stock_items,'stock_count':stock_count, 'total_sales_amount':total_sales_amount,'total_purchase_amount':total_purchase_amount,'unread_notifications_count':unread_notifications_count})



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



            ############       Create Clients Views         ############   
@login_required
def supplier(request):
    supplier = Supplier.objects.all()
    return render(request, 'clients/supplier/index.html', {'suppliers':supplier})

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


                    ################    Stock Item    #######################
@login_required
def add_stock_item(request):
    stock_form = StockItemForm()
    preform_type = Preform_type.objects.all()
    cap = Cap.objects.all()
    supplier = Supplier.objects.all()
   
    
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
        return render(request, 'store/add_stock/index.html', {'stock_form': stock_form, 'preform_types': preform_type, 'caps': cap, 'suppliers': supplier, 'color':color})


@login_required
def purchase_history(request):
    stock = StockItem.objects.order_by('-created_at')  # Order by the 'created_at' field in descending order
    return render(request, 'store/add_stock/details.html', {'stock': stock})

threshold_values = {
            'Cap': 5000,
            'Preform': 5000,
            'Bottle': 3000,
            'Shrinkwrapper': 30,  # Define a threshold value for "Shrinkwrapper"
            }

@login_required
def stock_detail(request):
    # Get all stock items
    updated_stock_items = Stock.objects.all()

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

    # Retrieve the updated stock items after deletion
    stock_items = Stock.objects.all().order_by('-id')
    notifications = Notification.objects.all()
    unread_notifications_count = notifications.filter(is_read=False).count()

    # Get the count of stock items
    stock_count = stock_items.count()

    return render(request, 'stock/index.html', {'stock_item': stock_items, 'stock_count': stock_count,'unread_notifications_count':unread_notifications_count})



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
    record = Production.objects.order_by('-created_at') 
    notifications = Notification.objects.all()
    unread_notifications_count = notifications.filter(is_read=False).count()
    return render(request, 'production/summary.html', {'record': record,'unread_notifications_count':unread_notifications_count })

@login_required
def sales_record(request):
    sales = Sales.objects.all()
    notifications = Notification.objects.all()
    unread_notifications_count = notifications.filter(is_read=False).count()
    return render(request, 'sales/index.html', {'sales': sales,'unread_notifications_count':unread_notifications_count})


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
        
        try:
            # Start a database transaction
            with transaction.atomic():
                # Deduct product quantity used from stock
                product.unit -= quantity
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
                return redirect('product')
        # Check if the form is for adding a new Cap type
        elif 'add_cap' in request.POST:
            cap_name = request.POST.get('cap_name')
            cap_size = request.POST.get('cap_size')
            cap_quantity_per_bag = request.POST.get('cap_quantity_per_bag')
            if cap_name and cap_size and cap_quantity_per_bag:
                Cap.objects.create(
                    name=cap_name,
                    size=cap_size,
                    quantity_per_bag=cap_quantity_per_bag
                )
                return redirect('product')

    preform_type = Preform_type.objects.all()
    cap = Cap.objects.all()

    return render(request, 'settings/product.html', {'preform_type': preform_type, 'cap': cap})

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
    