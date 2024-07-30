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
            return render(request, 'inventory/inventory_ticket_form.html', {'inventories': inventories})

        # Ensure the inventory exists
        try:
            inventory = Inventory.objects.get(pk=inventory_id)
        except Inventory.DoesNotExist:
            messages.error(request, 'Invalid inventory selection.')
            return render(request, 'inventory/inventory_ticket_form.html', {'inventories': inventories})

        try:
            # Convert numeric fields to Decimal and validate
            quantity = Decimal(quantity)
            if quantity <= 0:
                raise ValueError
        except (ValueError, InvalidOperation):
            messages.error(request, 'Quantity must be a positive numeric value.')
            return render(request, 'inventory/inventory_ticket_form.html', {'inventories': inventories})

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
                return render(request, 'inventory/inventory_ticket_form.html', {'inventories': inventories})
            inventory.unit -= quantity

        inventory.save()
        messages.success(request, 'Inventory ticket created and inventory updated successfully.')
        return redirect('inventory_list')

    # Render the form template for GET requests
    return render(request, 'inventory/inventory_ticket_form.html', {'inventories': inventories})




































def generate_report_view(request):
    # Get data for last month and current month
    today = datetime.today()
    first_day_of_this_month = today.replace(day=1)
    last_month = first_day_of_this_month - timedelta(days=1)
    first_day_of_last_month = last_month.replace(day=1)
    
    # Last month's data
    last_month_purchases = Purchase.objects.filter(created_at__month=last_month.month, created_at__year=last_month.year)
    last_month_sales = Sale.objects.filter(created_at__month=last_month.month, created_at__year=last_month.year)
    last_month_productions = Production.objects.filter(created_at__month=last_month.month, created_at__year=last_month.year)
    last_month_expenses = Expense.objects.filter(created_at__month=last_month.month, created_at__year=last_month.year)

    # Current month's data
    this_month_purchases = Purchase.objects.filter(created_at__month=today.month, created_at__year=today.year)
    this_month_sales = Sale.objects.filter(created_at__month=today.month, created_at__year=today.year)
    this_month_productions = Production.objects.filter(created_at__month=today.month, created_at__year=today.year)
    this_month_expenses = Expense.objects.filter(created_at__month=today.month, created_at__year=today.year)

    # Totals for summary
    total_last_month_sales = sum(sale.total for sale in last_month_sales)
    total_last_month_purchases = sum(purchase.total for purchase in last_month_purchases)
    total_last_month_productions = sum(prod.bottle_produced for prod in last_month_productions)
    total_last_month_expenses = sum(expense.amount for expense in last_month_expenses)
    
    total_this_month_sales = sum(sale.total for sale in this_month_sales)
    total_this_month_purchases = sum(purchase.total for purchase in this_month_purchases)
    total_this_month_productions = sum(prod.bottle_produced for prod in this_month_productions)
    total_this_month_expenses = sum(expense.amount for expense in this_month_expenses)

    # Financial calculations
    gross_profit = total_this_month_sales - total_this_month_purchases
    net_profit = gross_profit - total_this_month_expenses

    # Generate PDF report
    buffer = io.BytesIO()
    generate_pdf(buffer, last_month, today, total_last_month_sales, total_last_month_purchases, 
                 total_last_month_productions, total_last_month_expenses, total_this_month_sales, 
                 total_this_month_purchases, total_this_month_productions, total_this_month_expenses, 
                 gross_profit, net_profit, last_month_sales, last_month_purchases, last_month_productions,last_month_expenses 
                 )
    buffer.seek(0)

    # Send PDF via email
    send_report_email("user@example.com", buffer)

    # Return response
    return HttpResponse("Report generated and sent via email.")

def generate_pdf(buffer, last_month, today, total_last_month_sales, total_last_month_purchases, 
                 total_last_month_productions, total_last_month_expenses, total_this_month_sales, 
                 total_this_month_purchases, total_this_month_productions, total_this_month_expenses, 
                 gross_profit, net_profit, last_month_sales, last_month_purchases, last_month_productions, 
                 last_month_expenses):
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # First page - Summary
    c.drawString(100, 750, f"Monthly Inventory Report")
    c.drawString(100, 735, "-------------------------")
    c.drawString(100, 715, f"Summary for {last_month.strftime('%B %Y')}")
    c.drawString(100, 700, f"Total Sales: ${total_last_month_sales}")
    c.drawString(100, 685, f"Total Purchases: ${total_last_month_purchases}")
    c.drawString(100, 670, f"Bottles Produced: {total_last_month_productions}")
    c.drawString(100, 655, f"Total Expenses: ${total_last_month_expenses}")
    c.drawString(100, 635, f"Summary for {today.strftime('%B %Y')}")
    c.drawString(100, 620, f"Total Sales: ${total_this_month_sales}")
    c.drawString(100, 605, f"Total Purchases: ${total_this_month_purchases}")
    c.drawString(100, 590, f"Bottles Produced: {total_this_month_productions}")
    c.drawString(100, 575, f"Total Expenses: ${total_this_month_expenses}")

    c.showPage()

    # Detailed pages
    # Sales
    y = 750
    c.drawString(100, y, "Sales Report")
    y -= 20

    # Sales chart
    sales_chart_data = [(sale.product.name, sale.quantity) for sale in last_month_sales]
    sales_chart = VerticalBarChart()
    sales_chart.x = 50
    sales_chart.y = 500
    sales_chart.height = 200
    sales_chart.width = 400
    sales_chart.data = [[item[1] for item in sales_chart_data]]
    sales_chart.categoryAxis.categoryNames = [item[0] for item in sales_chart_data]
    sales_chart.bars.fillColor = colors.green
    renderPDF.draw(sales_chart, c, 0, 500)
    y = 480
    c.drawString(100, y, "Product Details")
    y -= 20
    for sale in last_month_sales:
        c.drawString(100, y, f"{sale.product.name}: {sale.quantity} units - Total: ${sale.total}")
        y -= 20
    c.drawString(100, y, f"Grand Total Sales: ${total_last_month_sales}")
    c.showPage()

    # Purchases
    y = 750
    c.drawString(100, y, "Purchases Report")
    y -= 20

    # Purchases chart
    purchases_chart_data = [(purchase.product.name, purchase.quantity) for purchase in last_month_purchases]
    purchases_chart = VerticalBarChart()
    purchases_chart.x = 50
    purchases_chart.y = 500
    purchases_chart.height = 200
    purchases_chart.width = 400
    purchases_chart.data = [[item[1] for item in purchases_chart_data]]
    purchases_chart.categoryAxis.categoryNames = [item[0] for item in purchases_chart_data]
    purchases_chart.bars.fillColor = colors.blue
    renderPDF.draw(purchases_chart, c, 0, 500)
    y = 480
    c.drawString(100, y, "Product Details")
    y -= 20
    for purchase in last_month_purchases:
        c.drawString(100, y, f"{purchase.product.name}: {purchase.quantity} units - Total: ${purchase.total}")
        y -= 20
    c.drawString(100, y, f"Grand Total Purchases: ${total_last_month_purchases}")
    c.showPage()

    # Production
    y = 750
    c.drawString(100, y, "Production Report")
    y -= 20

    # Production chart
    production_chart_data = [(prod.product.name, prod.bottle_produced) for prod in last_month_productions]
    production_chart = VerticalBarChart()
    production_chart.x = 50
    production_chart.y = 500
    production_chart.height = 200
    production_chart.width = 400
    production_chart.data = [[item[1] for item in production_chart_data]]
    production_chart.categoryAxis.categoryNames = [item[0] for item in production_chart_data]
    production_chart.bars.fillColor = colors.orange
    renderPDF.draw(production_chart, c, 0, 500)
    y = 480
    c.drawString(100, y, "Product Details")
    y -= 20
    for prod in last_month_productions:
        c.drawString(100, y, f"{prod.product.name}: {prod.bottle_produced} bottles produced")
        y -= 20
    c.drawString(100, y, f"Total Bottles Produced: {total_last_month_productions}")
    c.showPage()

    # Expenses
    y = 750
    c.drawString(100, y, "Expenses Report")
    y -= 20
    for expense in last_month_expenses:
        c.drawString(100, y, f"{expense.description}: ${expense.amount}")
        y -= 20
    c.drawString(100, y, f"Total Expenses: ${total_last_month_expenses}")
    c.showPage()

    # Balance Sheet
    y = 750
    c.drawString(100, y, "Balance Sheet")
    y -= 20
    c.drawString(100, y, f"Total Revenue: ${total_this_month_sales}")
    y -= 20
    c.drawString(100, y, f"Total Cost of Goods Sold: ${total_this_month_purchases}")
    y -= 20
    c.drawString(100, y, f"Gross Profit: ${gross_profit}")
    y -= 20
    c.drawString(100, y, f"Total Expenses: ${total_this_month_expenses}")
    y -= 20
    c.drawString(100, y, f"Net Profit: ${net_profit}")
    c.showPage()

    c.save()

def send_report_email(to_email, pdf_buffer):
    subject = "Monthly Inventory Report"
    body = "Please find attached the inventory report for this month."
    email = EmailMessage(subject, body, 'eniolaemmanuel@gmail.com', [to_email])
    email.attach('report.pdf', pdf_buffer.getvalue(), 'application/pdf')
    email.send()