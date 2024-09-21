import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout 
from django.contrib import messages
from old_stock.models import Old_Stock
from sale.models import Sale, Customer
from django.db.models.functions import ExtractMonth
from purchase.models import Inventory, Purchase
from production.models import Production
from .models import InventoryTicket, Expense
from datetime import datetime,  timedelta
from django.utils import timezone  
from decimal import Decimal, InvalidOperation
from decimal import Decimal
from django.middleware.csrf import rotate_token
from django.urls import reverse
from decimal import Decimal
from datetime import datetime
from calendar import monthrange
import calendar
from django.core.paginator import Paginator
###############     Create your views here    ###############

from django.db.models import Sum


def home(request):
    # Get the current date and time
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    today = timezone.now()
    
    # Sum the total quantity of excesses (INCREASE) for the current month
    total_excesses_quantity = InventoryTicket.objects.filter(
        created_at__year=today.year,
        created_at__month=today.month,
        reason='INCREASE'
    ).aggregate(total_excess=Sum('quantity'))['total_excess'] or 0

    # Sum the total quantity of shortages (DECREASE) for the current month
    total_shortages_quantity = InventoryTicket.objects.filter(
        created_at__year=today.year,
        created_at__month=today.month,
        reason='DECREASE'
    ).aggregate(total_shortage=Sum('quantity'))['total_shortage'] or 0

    # Total sales, purchases, old stock, and other metrics for the current month
    total_sales = Sale.objects.filter(created_at__year=current_year, created_at__month=current_month).aggregate(total_sales_price=Sum('total'))['total_sales_price'] or 0
    total_purchases = Purchase.objects.filter(created_at__year=current_year, created_at__month=current_month).aggregate(total_purchase_price=Sum('total'))['total_purchase_price'] or 0
    total_old_stock = Old_Stock.objects.filter(created_at__year=current_year, created_at__month=current_month).aggregate(total_old_stock_price=Sum('price'))['total_old_stock_price'] or 0
    total_purchases += total_old_stock
    total_produced_bottles = Production.objects.filter(production_date__year=current_year, production_date__month=current_month).aggregate(total_bottles=Sum('produced_bottles'))['total_bottles'] or 0
    total_inventory = Inventory.objects.aggregate(total_products=Sum('unit'))['total_products'] or 0

    # Specific product totals in inventory
    total_preform_inventory = Inventory.objects.filter(product__name='preform').aggregate(total_preform=Sum('unit'))['total_preform'] or 0
    total_cap_inventory = Inventory.objects.filter(product__name='cap').aggregate(total_cap=Sum('unit'))['total_cap'] or 0
    total_bottle_inventory = Inventory.objects.filter(product__name='bottle').aggregate(total_bottle=Sum('unit'))['total_bottle'] or 0
    total_shrinkwrapper_inventory = Inventory.objects.filter(product__name='shrinkwrapper').aggregate(total_shrinkwrapper=Sum('unit'))['total_shrinkwrapper'] or 0
    

    today = timezone.now()
    start_of_year = today.replace(month=1, day=1)
    end_of_year = today.replace(month=12, day=31)

    # Query for sales
    sales = (Sale.objects
             .filter(created_at__range=(start_of_year, end_of_year))
             .annotate(month=ExtractMonth('created_at'))
             .values('month')
             .annotate(total_units=Sum('unit'))
             .order_by('month'))

    # Query for purchases
    purchases = (Purchase.objects
                 .filter(created_at__range=(start_of_year, end_of_year))
                 .annotate(month=ExtractMonth('created_at'))
                 .values('month')
                 .annotate(total_units=Sum('unit'))
                 .order_by('month'))

    # Create a list of labels for each month of the year
    sales_labels = [calendar.month_name[i] for i in range(1, 13)]
    
    # Sum the total price of expenses for the current month
    total_expenses_price = Expense.objects.filter(
        created_at__year=today.year,
        created_at__month=today.month
    ).aggregate(total_spent=Sum('price'))['total_spent'] or 0
    
    # Create lists of sales and purchases data for each month
    sales_data = [0] * 12
    purchases_data = [0] * 12
    
    for sale in sales:
        sales_data[sale['month'] - 1] = float(sale['total_units'])

    for purchase in purchases:
        purchases_data[purchase['month'] - 1] = float(purchase['total_units'])

    low_inventory_items = Inventory.objects.filter(unit__lte=500).order_by('unit')[:5]

    if not low_inventory_items.exists():
        low_inventory_items = None



     # Aggregate total units for each product using filter
    product_totals = Inventory.objects.filter(product__name__in=['preform', 'cap', 'bottle', 'shrinkwrapper']) \
        .values('product__name') \
        .annotate(total_units=Sum('unit'))

    # Initialize the totals for each product as Decimal
    total_preform_inventory = Decimal(0)
    total_cap_inventory = Decimal(0)
    total_bottle_inventory = Decimal(0)
    total_shrinkwrapper_inventory = Decimal(0)


    # Query for defective preforms and bottles in the current month
    defective_data = Production.objects.filter(
        production_date__year=today.year,
        production_date__month=today.month
    ).aggregate(
        total_defective_preforms=Sum('defective_preforms'),
        total_defective_bottles=Sum('defective_bottles')
    )

    # Extract the results
    bad_preforms = defective_data['total_defective_preforms'] or 0
    bad_bottles = defective_data['total_defective_bottles'] or 0

    # Assign totals from query result
    for product in product_totals:
        if product['product__name'] == 'preform':
            total_preform_inventory = product['total_units']
        elif product['product__name'] == 'cap':
            total_cap_inventory = product['total_units']
        elif product['product__name'] == 'bottle':
            total_bottle_inventory = product['total_units']
        elif product['product__name'] == 'shrinkwrapper':
            total_shrinkwrapper_inventory = product['total_units']

    # Data to be passed to template - converting to float
    labels = ['Preform', 'Cap', 'Bottle', 'Shrinkwrapper']
    data = [
        float(total_preform_inventory),
        float(total_cap_inventory),
        float(total_bottle_inventory),
        float(total_shrinkwrapper_inventory)
    ]

    context = {
        'total_sales': total_sales,
        'total_purchases': total_purchases,
        'total_produced_bottles': total_produced_bottles,
        'total_inventory': total_inventory,
        'total_preform_inventory': total_preform_inventory,
        'total_cap_inventory': total_cap_inventory,
        'total_bottle_inventory': total_bottle_inventory,
        'total_shrinkwrapper_inventory': total_shrinkwrapper_inventory,
        'sales_labels': sales_labels,
        'sales_data': sales_data,
        'purchases_data': purchases_data,
        'low_inventory_items': low_inventory_items,
        'labels': labels,
        'data': data,
        'today':today,
        'bad_preforms':bad_preforms,
        'bad_bottles':bad_bottles,
        'total_shortages_quantity':total_shortages_quantity,
        'total_excesses_quantity':total_excesses_quantity,
        'total_expenses_price':total_expenses_price
    }

    return render(request, 'base/home.html', context)


def sales_purchases_chart(request):
     # Aggregate total units for each product using filter
    product_totals = Inventory.objects.filter(product__name__in=['preform', 'cap', 'bottle', 'shrinkwrapper']) \
        .values('product__name') \
        .annotate(total_units=Sum('unit'))

    # Initialize the totals for each product as Decimal
    total_preform_inventory = Decimal(0)
    total_cap_inventory = Decimal(0)
    total_bottle_inventory = Decimal(0)
    total_shrinkwrapper_inventory = Decimal(0)

    # Assign totals from query result
    for product in product_totals:
        if product['product__name'] == 'preform':
            total_preform_inventory = product['total_units']
        elif product['product__name'] == 'cap':
            total_cap_inventory = product['total_units']
        elif product['product__name'] == 'bottle':
            total_bottle_inventory = product['total_units']
        elif product['product__name'] == 'shrinkwrapper':
            total_shrinkwrapper_inventory = product['total_units']

    # Data to be passed to template - converting to float
    labels = ['Preform', 'Cap', 'Bottle', 'Shrinkwrapper']
    data = [
        float(total_preform_inventory),
        float(total_cap_inventory),
        float(total_bottle_inventory),
        float(total_shrinkwrapper_inventory)
    ]

    # Pass labels and data to the template
    context = {
        'labels': labels,
        'data': data
    }


    return render(request, 'base/chart.html', context)

def csrf_failure_view(request, reason=""):
    # You can customize this view to render a custom template or redirect users
    return render(request, 'base/login.html', {'reason': reason})


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


@login_required
def invoice(request):
    error = None
    sales_data = None
    customers = Customer.objects.all()
    
    if request.method == 'GET':
        customer_str = request.GET.get('customer')
        transaction_date_str = request.GET.get('transaction_date')

        if customer_str and transaction_date_str:
            try:
                transaction_date = datetime.strptime(transaction_date_str, '%Y-%m-%d').date()
                
                sales_data = Sale.objects.filter(customer__name=customer_str, created_at__date=transaction_date)
                
                if not sales_data:
                    error = 'No sales found for the selected criteria.'
            except ValueError:
                error = 'Invalid date format. Please use YYYY-MM-DD.'

    return render(request, 'invoice/base.html', {'sales_data': sales_data, 'customers': customers, 'error': error})

@login_required  
def print_invoice(request):
    if request.method == 'GET':
        selected_sales_ids = request.GET.getlist('selected_sales')
        sales_data = Sale.objects.filter(id__in=selected_sales_ids)
        
        sum_total = sum(sale.total for sale in sales_data)
        return render(request, 'invoice/index.html', {'sales_data': sales_data, 'sum_total': sum_total})

    else:
        pass


@login_required
def settings(request):
    return render(request, 'settings/index.html')


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


def inventory_ticket_create_view(request):
    inventories = Inventory.objects.all()

    if request.method == 'POST':
        # Retrieve data from POST request
        inventory_id = request.POST.get('inventory')
        quantity = request.POST.get('quantity')
        reason = request.POST.get('reason')
        note = request.POST.get('note')

        # Validate data
        if not inventory_id or not quantity or not reason:
            messages.error(request, 'Inventory, quantity, and reason are required.')
            return render(request, 'settings/ticket.html', {'inventories': inventories})

        # Ensure the inventory exists
        try:
            inventory = Inventory.objects.get(pk=inventory_id)
        except Inventory.DoesNotExist:
            messages.error(request, 'Invalid inventory selection.')
            return render(request, 'settings/ticket.html', {'inventories': inventories})

        try:
            # Convert numeric fields to Decimal and validate
            quantity = Decimal(quantity)
            if quantity <= 0:
                raise ValueError
        except (ValueError, InvalidOperation):
            messages.error(request, 'Quantity must be a positive numeric value.')
            return render(request, 'settings/ticket.html', {'inventories': inventories})

        # Create InventoryTicket instance
        ticket = InventoryTicket.objects.create(
            inventory=inventory,
            quantity=quantity,
            reason=reason,
            note=note,
        )

        # Adjust inventory based on reason
        if reason == 'INCREASE':
            inventory.unit += quantity
        elif reason == 'DECREASE':
            if inventory.unit < quantity:
                messages.error(request, 'Not enough units in inventory to decrease by the specified quantity.')
                return render(request, 'settings/ticket.html', {'inventories': inventories})
            inventory.unit -= quantity

        inventory.save()
        messages.success(request, 'Inventory ticket created and inventory updated successfully.')
        return redirect('inventory_list')

    # Render the form template for GET requests
    return render(request, 'settings/ticket.html', {'inventories': inventories})




def inventory_ticket_list(request):
    tickets = InventoryTicket.objects.select_related('inventory__product').order_by('-created_at')


    context = {
        'tickets': tickets,
    }
    return render(request, 'settings/inventory_ticket_list.html', context)


                ###### EXPENSES   ########

def create_expense(request):
    if request.method == 'POST':
        # Extract data from the form
        created_at = request.POST.get('created_at')
        price = request.POST.get('price')
        category = request.POST.get('category')
        description = request.POST.get('description')
        
        # Create a new Expense object and save it
        expense = Expense(
            price=price,
            category=category,
            description=description,
            created_at=created_at  # Using current time for simplicity
        )
        expense.save()
        return redirect('expense_list')  # Redirect to the list of expenses
    
    return render(request, 'expenses/create_expense.html')  

def expense_list(request):
    expenses = Expense.objects.all()  # Fetch all Expense objects
    
    # Set up pagination (10 expenses per page in this example)
    paginator = Paginator(expenses, 10)
    page_number = request.GET.get('page')  # Get the page number from the request
    page_obj = paginator.get_page(page_number)  # Get the page of expenses
    
    return render(request, 'expenses/expense_list.html', {'page_obj': page_obj})


def update_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)  # Fetch the Expense object

    if request.method == 'POST':
        # Update the Expense object with new data
        expense.price = request.POST.get('price')
        expense.category = request.POST.get('category')
        expense.description = request.POST.get('description')  # Fix typo here
        expense.created_at = request.POST.get('created_at')  # Add if necessary
        expense.save()
        return redirect('expense_list')  # Redirect to the list of expenses

    return render(request, 'expenses/update_expense.html', {'expense': expense})

def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    
    if request.method == 'POST':
        expense.delete()
        return redirect('expense_list')  # Redirect to the list of expenses

    return render(request, 'expenses/expense_list.html', {'expense': expense})








