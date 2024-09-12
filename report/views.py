from django.shortcuts import render,redirect
from django.db.models import Sum, F
from django.utils import timezone
from django.urls import reverse
from product.models import Product
from sale.models import Sale
from production.models import Production
from purchase.models import Purchase, Inventory
from old_stock.models import Old_Stock 
from store.models import Expense , InventoryTicket
from datetime import datetime, timedelta
from decimal import Decimal
import random
import string

def business_statement(request):
    # Get the date range from the request, convert them to timezone-aware datetimes
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    if start_date_str:
        start_date = timezone.make_aware(timezone.datetime.strptime(start_date_str, '%Y-%m-%d'), timezone.get_current_timezone())
    else:
        start_date = timezone.localtime(timezone.now()).replace(hour=0, minute=0, second=0, microsecond=0)

    if end_date_str:
        end_date = timezone.make_aware(timezone.datetime.strptime(end_date_str, '%Y-%m-%d'), timezone.get_current_timezone())
    else:
        end_date = timezone.localtime(timezone.now()).replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Get all products
    products = Product.objects.all()
    
    statement = []
    
    for product in products:
        # Total purchases within the date range
        total_purchased_units = Purchase.objects.filter(
            product=product,
            created_at__range=[start_date, end_date]
        ).aggregate(total_units=Sum('unit'))['total_units'] or 0
        
        # Total old stock entries within the date range
        total_oldstock_units = Old_Stock.objects.filter(
            product=product,
            created_at__range=[start_date, end_date]
        ).aggregate(total_units=Sum('unit'))['total_units'] or 0
        
        # Total sales within the date range
        total_sold_units = Sale.objects.filter(
            product=product,
            created_at__range=[start_date, end_date]
        ).aggregate(total_units=Sum('unit'))['total_units'] or 0
        
        # Total units used in production within the date range
        total_used_in_production = Production.objects.filter(
            preform_product__product=product,
            production_date__range=[start_date, end_date]
        ).aggregate(total_units=Sum('used_preforms'))['total_units'] or 0
        
        # Total units produced from this product (bottles) within the date range
        total_produced_units = Production.objects.filter(
            produced_bottle_product=product,
            production_date__range=[start_date, end_date]
        ).aggregate(total_units=Sum('produced_bottles'))['total_units'] or 0
        
        # Calculate the balance
        balance_units = total_purchased_units + total_oldstock_units + total_produced_units - total_sold_units - total_used_in_production
        
        # Get inventory units from the Inventory model
        try:
            inventory = Inventory.objects.get(product=product)
            inventory_units = inventory.unit
        except Inventory.DoesNotExist:
            inventory_units = 0
        
        statement.append({
            'product': product.name,
            'product_type': product.type.name if product.type else '',
            'size': product.size,
            'color': product.color.name if product.color else '',
            'unit': product.unit,
            'purchased_units': total_purchased_units,
            'oldstock_units': total_oldstock_units,
            'sold_units': total_sold_units,
            'used_in_production_units': total_used_in_production,
            'produced_units': total_produced_units,
            'balance_units': balance_units,
            'inventory_units': inventory_units,
        })
    
    context = {
        'statement': statement,
        'start_date': start_date.date(),
        'end_date': end_date.date(),
    }
    
    return render(request, 'business_statement.html', context)


def business_report_view(request):
    # Generate list of months and years
    current_year = datetime.now().year
    start_year = 2000
    end_year = 2100
    years = list(range(start_year, end_year + 1))

    # Pass months and years to the template
    context = {
        'months': [
            {'value': 1, 'name': 'January'},
            {'value': 2, 'name': 'February'},
            {'value': 3, 'name': 'March'},
            {'value': 4, 'name': 'April'},
            {'value': 5, 'name': 'May'},
            {'value': 6, 'name': 'June'},
            {'value': 7, 'name': 'July'},
            {'value': 8, 'name': 'August'},
            {'value': 9, 'name': 'September'},
            {'value': 10, 'name': 'October'},
            {'value': 11, 'name': 'November'},
            {'value': 12, 'name': 'December'},
        ],
        'years': years,
        'current_year': current_year
    }

    if request.method == 'POST':
        # Get the form data directly from the request.POST dictionary
        report_type = request.POST.get('report_type')
        month = request.POST.get('month')
        year = request.POST.get('year')
        
        # Redirect to the appropriate report detail page based on report type
        if report_type == 'sales':
            return redirect(reverse('sales_report', args=[month, year]))
        elif report_type == 'purchases':
            return redirect(reverse('purchases_report', args=[month, year]))
        elif report_type == 'production':
            return redirect(reverse('production_report', args=[month, year]))
        elif report_type == 'business':
            return redirect(reverse('business_report_view', args=[month, year]))
        else:
            # Handle invalid report type if needed
            return redirect('error_page')  # Or another appropriate page

    return render(request, 'business_report.html', context)





def sales_report(request, month, year):
    month = int(month)
    year = int(year)

    # Aggregate sales by product, summing up the total quantity and total price
    sales_data = (
        Sale.objects.filter(created_at__year=year, created_at__month=month)
        .values('product')
        .annotate(total_quantity_sold=Sum('quantity'), total_price_sold=Sum('total'))
    )
    
    # Retrieve Product instances for each product ID in sales_data
    product_ids = [sale['product'] for sale in sales_data]
    products = Product.objects.filter(id__in=product_ids)

    # Create a dictionary of Product instances keyed by their IDs
    product_dict = {product.id: product for product in products}

    # Replace product ID with actual Product instance in sales_data
    for sale in sales_data:
        sale['product'] = product_dict[sale['product']]

    # Calculate the grand total of all sales units and prices
    total_units_sold = sales_data.aggregate(total_units_sold=Sum('total_quantity_sold'))['total_units_sold'] or 0
    total_sales_price = sales_data.aggregate(total_sales_price=Sum('total_price_sold'))['total_sales_price'] or 0

    context = {
        'month': month,
        'year': year,
        'sales_data': sales_data,
        'total_units_sold': total_units_sold,
        'total_sales_price': total_sales_price,
    }

    return render(request, 'sales_report.html', context)


def purchases_report(request, month, year):
    month = int(month)
    year = int(year)

    # Aggregate purchases by product, summing up the total quantity and total price
    purchases_data = (
        Purchase.objects.filter(created_at__year=year, created_at__month=month)
        .values('product')
        .annotate(
            total_quantity_purchased=Sum('quantity'),
            total_price_purchased=Sum('total')
        )
    )

    # Retrieve Product instances for each product ID in purchases_data
    product_ids = [purchase['product'] for purchase in purchases_data]
    products = Product.objects.filter(id__in=product_ids)

    # Create a dictionary of Product instances keyed by their IDs
    product_dict = {product.id: product for product in products}

    # Replace product ID with actual Product instance in purchases_data
    for purchase in purchases_data:
        purchase['product'] = product_dict[purchase['product']]

    # Calculate the grand total of all purchased units and prices
    total_units_purchased = purchases_data.aggregate(total_units_purchased=Sum('total_quantity_purchased'))['total_units_purchased'] or 0
    total_purchase_price = purchases_data.aggregate(total_purchase_price=Sum('total_price_purchased'))['total_purchase_price'] or 0

    context = {
        'month': month,
        'year': year,
        'title': 'Purchases Summary Report',
        'purchases_data': purchases_data,
        'total_units_purchased': total_units_purchased,
        'total_purchase_price': total_purchase_price,
    }

    return render(request, 'purchases_report.html', context)


def production_report(request, month, year):
    month = int(month)
    year = int(year)

    # Aggregate production by preform product, summing up the total used preforms and defective preforms
    preform_data = (
        Production.objects.filter(production_date__year=year, production_date__month=month)
        .values('preform_product')
        .annotate(
            total_used_preforms=Sum('used_preforms'),
            total_defective_preforms=Sum('defective_preforms')
        )
    )

    # Retrieve Product instances for each preform product ID in preform_data
    preform_product_ids = [data['preform_product'] for data in preform_data]
    preform_products = Inventory.objects.filter(id__in=preform_product_ids)

    # Create a dictionary of Inventory instances keyed by their IDs
    preform_product_dict = {product.id: product for product in preform_products}

    # Replace product ID with actual Inventory instance in preform_data
    for data in preform_data:
        data['preform_product'] = preform_product_dict[data['preform_product']]

    # Aggregate production by produced bottle product, summing up the total produced bottles and defective bottles
    bottle_data = (
        Production.objects.filter(production_date__year=year, production_date__month=month)
        .values('produced_bottle_product')
        .annotate(
            total_produced_bottles=Sum('produced_bottles'),
            total_defective_bottles=Sum('defective_bottles')
        )
    )

    # Retrieve Product instances for each bottle product ID in bottle_data
    bottle_product_ids = [data['produced_bottle_product'] for data in bottle_data]
    bottle_products = Product.objects.filter(id__in=bottle_product_ids)

    # Create a dictionary of Product instances keyed by their IDs
    bottle_product_dict = {product.id: product for product in bottle_products}

    # Replace product ID with actual Product instance in bottle_data
    for data in bottle_data:
        data['produced_bottle_product'] = bottle_product_dict[data['produced_bottle_product']]

    # Calculate the grand total of all preform quantities and defective preforms
    total_used_preforms = sum(data['total_used_preforms'] for data in preform_data)
    total_defective_preforms = sum(data['total_defective_preforms'] for data in preform_data)

    # Calculate the grand total of all produced bottles and defective bottles
    total_produced_bottles = sum(data['total_produced_bottles'] for data in bottle_data)
    total_defective_bottles = sum(data['total_defective_bottles'] for data in bottle_data)

    context = {
        'month': month,
        'year': year,
        'title': 'Production Summary Report',
        'preform_data': preform_data,
        'bottle_data': bottle_data,
        'total_used_preforms': total_used_preforms,
        'total_defective_preforms': total_defective_preforms,
        'total_produced_bottles': total_produced_bottles,
        'total_defective_bottles': total_defective_bottles,
    }

    return render(request, 'production_report.html', context)





def business_report_detail_view(request, month, year):
    try:
        # Convert month and year to integers
        month = int(month)
        year = int(year)
     
        # Validate month and year values
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12")
        
        if year < 1900 or year > 2100:  # Example range for year validation
            raise ValueError("Year is out of range")

        # Define the start and end date for the given month and year
        start_date = timezone.make_aware(datetime(year, month, 1))
        # Calculate the last day of the month
        next_month = month % 12 + 1
        next_year = year if month < 12 else year + 1
        end_date = timezone.make_aware(datetime(next_year, next_month, 1) - timedelta(days=1))

        # Initialize totals
        total_sales_sum = Decimal(0)
        total_purchases_sum = Decimal(0)
        total_expenses_sum = Expense.objects.filter(
            created_at__range=[start_date, end_date]
        ).aggregate(total_expenses=Sum('price'))['total_expenses'] or Decimal(0)

        # Initialize lists for totals
        inventory_totals = []
        purchased_totals = []
        purchase_price_totals = []
        sold_totals = []
        sales_price_totals = []
        used_totals = []
        defective_preforms_totals = []
        produced_totals = []
        defective_bottles_totals = []
        excesses_totals = []
        shortages_totals = []

         # Initialize the report_data list
        report_data = []
        # Get all products
        products = Product.objects.all()
        
        for product in products:
            # Calculate inventory quantity
            inventory = Inventory.objects.filter(product=product).aggregate(total_inventory=Sum('unit'))['total_inventory'] or Decimal(0)

            # Calculate total sold and total sales price
            sales = Sale.objects.filter(product=product, created_at__range=[start_date, end_date]).aggregate(
                total_sold=Sum('unit'),
                total_sales_price=Sum('total')
            )
            total_sold = sales['total_sold'] or Decimal(0)
            total_sales_price = sales['total_sales_price'] or Decimal(0)
            total_sales_sum += total_sales_price  # Sum the total sales price
            
            # Calculate total purchased and total purchase price
            purchases = Purchase.objects.filter(product=product, created_at__range=[start_date, end_date]).aggregate(
                total_purchased=Sum('unit'),
                total_purchase_price=Sum('total')
            )
            old_stock = Old_Stock.objects.filter(product=product, created_at__range=[start_date, end_date]).aggregate(
                total_old_stock=Sum('unit'),
                total_old_stock_price=Sum('price')
            )

            total_purchased = (purchases['total_purchased'] or Decimal(0)) + (old_stock['total_old_stock'] or Decimal(0))
            total_purchase_price = (purchases['total_purchase_price'] or Decimal(0)) + (old_stock['total_old_stock_price'] or Decimal(0))
            total_purchases_sum += total_purchase_price  # Sum the total purchase price

            # Calculate total quantity used in production and quantity produced
            productions = Production.objects.filter(
                produced_bottle_product=product, 
                production_date__range=[start_date, end_date]
            ).aggregate(
                total_used=Sum('used_preforms'),
                total_produced=Sum('produced_bottles'),
                total_defective_preforms=Sum('defective_preforms'),
                total_defective_bottles=Sum('defective_bottles')
            )
            total_used = productions['total_used'] or Decimal(0)
            total_produced = productions['total_produced'] or Decimal(0)
            total_defective_preforms = productions['total_defective_preforms'] or Decimal(0)
            total_defective_bottles = productions['total_defective_bottles'] or Decimal(0)
            
            # Calculate excess or shortages based on InventoryTicket model
            excesses = InventoryTicket.objects.filter(
                inventory__product=product,
                reason='INCREASE',
                created_at__range=[start_date, end_date]
            ).aggregate(total_excess=Sum('quantity'))['total_excess'] or Decimal(0)

            shortages = InventoryTicket.objects.filter(
                inventory__product=product,
                reason='DECREASE',
                created_at__range=[start_date, end_date]
            ).aggregate(total_shortage=Sum('quantity'))['total_shortage'] or Decimal(0)

            # Append data to the report list
            report_data.append({
                'product': product,
                'inventory': inventory,
                'total_sold': total_sold,
                'total_sales_price': total_sales_price,
                'total_purchased': total_purchased,
                'total_purchase_price': total_purchase_price,
                'total_used': total_used,
                'total_produced': total_produced,
                'excesses': excesses,
                'shortages': shortages,
                'total_defective_preforms': total_defective_preforms,
                'total_defective_bottles': total_defective_bottles,
            })

            # Accumulate totals
            inventory_totals.append(inventory)
            purchased_totals.append(total_purchased)
            purchase_price_totals.append(total_purchase_price)
            sold_totals.append(total_sold)
            sales_price_totals.append(total_sales_price)
            used_totals.append(total_used)
            defective_preforms_totals.append(total_defective_preforms)
            produced_totals.append(total_produced)
            defective_bottles_totals.append(total_defective_bottles)
            excesses_totals.append(excesses)
            shortages_totals.append(shortages)

            

        # Aggregate totals manually for the context
        context = {
            'report_data': report_data,
            'selected_month': month,
            'selected_year': year,
            'total_sales_sum': total_sales_sum,
            'total_purchases_sum': total_purchases_sum,
            'total_expenses_sum': total_expenses_sum,
            'inventory_sum': sum(inventory_totals),
            'purchased_sum': sum(purchased_totals),
            'purchase_price_sum': sum(purchase_price_totals),
            'sold_sum': sum(sold_totals),
            'sales_price_sum': sum(sales_price_totals),
            'used_sum': sum(used_totals),
            'defective_preforms_sum': sum(defective_preforms_totals),
            'produced_sum': sum(produced_totals),
            'defective_bottles_sum': sum(defective_bottles_totals),
            'excesses_sum': sum(excesses_totals),
            'shortages_sum': sum(shortages_totals),
           
        }

        return render(request, 'report_detail.html', context)

    except ValueError as e:
        # Handle the value error (e.g., return an error response or render an error template)
        return render(request, 'report_detail.html', {'error_message': str(e)})
