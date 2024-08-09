from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout 
from django.contrib import messages
from sale.models import Sale, Customer

from purchase.models import Inventory, Purchase
from production.models import Production
from .models import InventoryTicket, Expense
from django.utils import timezone
import datetime
from decimal import Decimal, InvalidOperation
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from decimal import Decimal

from django.middleware.csrf import rotate_token

from django.urls import reverse

from django.core.mail import EmailMessage
from decimal import Decimal
from .models import Inventory
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics import renderPDF
import io
from datetime import datetime, timedelta


from calendar import monthrange

###############     Create your views here    ###############

def home(request):
    context = {
    }  
    return render(request, 'base/home.html', context)


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
            return redirect('inventory_list')
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










