from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from product.models import Product
from sale.models import Sale
from production.models import Production
from purchase.models import Purchase, Inventory
from old_stock.models import Old_Stock


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
