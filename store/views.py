from django.shortcuts import render, redirect, get_object_or_404
from .models import Ticket_Records, Notification
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout 
from django.contrib import messages
from sale.models import Sale
from sale.models import Customer

from django.utils import timezone
import datetime

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

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

    context = {
        
    }
    
    return render(request, 'base/home.html', context)

def csrf_failure_view(request, reason=""):
    # You can customize this view to render a custom template or redirect users
    return render(request, 'base/login.html', {'reason': reason})


# def error_page(request):
#     return render(request, 'base/test.html', {'user': request.user})

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
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        if customer_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
                
                sales_data = Sale.objects.filter(customer__name=customer_str)
                
                if start_date:
                    sales_data = sales_data.filter(created_at__gte=start_date)
                if end_date:
                    sales_data = sales_data.filter(created_at__lte=end_date)
                
                if not sales_data:
                    error = 'No sales found for the selected criteria.'
            except ValueError:
                error = 'Invalid date format. Please use YYYY-MM-DD.'

    return render(request, 'invoice/base.html', {'sales_data': sales_data, 'customers': customers, 'error': error})

@login_required  
def print_invoice(request):
    if request.method == 'GET':
        selected_sales_ids = request.GET.getlist('selected_sales')  # Get selected sales IDs from the query parameters
        sales_data = Sale.objects.filter(id__in=selected_sales_ids) 
        
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
