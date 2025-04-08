from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import PS_Inventory, PS_Production, PS_RawMaterialReceipt
from sale.models import Customer
from purchase.models import Product

# 1. Raw Material Entry Form
@login_required
def raw_material_entry(request):
    if request.method == 'POST':
        try:
            customer_id = request.POST.get('customer')  
            product_id = request.POST.get('product')  
            quantity_in_bags = int(request.POST.get('quantity_in_bags', 0))
            quantity_in_units = int(request.POST.get('quantity_in_units', 0))
            amount = request.POST.get('amount')
            date_received_str = request.POST.get('date_received')

            # Validate required fields
            if not all([customer_id, product_id, amount, date_received_str]):
                messages.error(request, "All fields are required.")
                return redirect('raw_material_entry')

            # Convert amount and discount to decimal
            amount = float(amount)
           
            # Convert date input
            try:
                date_received = timezone.datetime.strptime(date_received_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                messages.error(request, "Invalid date format. Use the correct format.")
                return redirect('raw_material_entry')

            # Get the selected customer and product
            customer = Customer.objects.get(pk=customer_id)
            product = Product.objects.get(pk=product_id)

            # Ensure the selected product is 'preform'
            if product.name.lower() != 'preform':
                messages.error(request, "Only preform products are allowed.")
                return redirect('raw_material_entry')

            # Create raw material entry
            raw_material = PS_RawMaterialReceipt.objects.create(
                customer=customer,
                product=product,
                quantity_in_bags=quantity_in_bags,
                quantity_in_units=quantity_in_units,
                amount=amount,
                date_received=date_received
            )

            messages.success(request, "Raw material added successfully.")
            return redirect('raw_material_history')

        except Customer.DoesNotExist:
            messages.error(request, "Selected customer does not exist.")
        except Product.DoesNotExist:
            messages.error(request, "Selected product does not exist.")
        except Exception as e:
            messages.error(request, f"Error processing request: {e}")

    # Fetch customers and preform products for the dropdown
    customers = Customer.objects.all()
    preform_products = Product.objects.filter(name='preform')

    return render(request, 'raw_material_entry.html', {'customers': customers, 'preform_products': preform_products})

# 2. Raw Material History Table
@login_required
def raw_material_history(request):
    raw_materials = PS_RawMaterialReceipt.objects.all().order_by('-date_received')
    paginator = Paginator(raw_materials, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'raw_material_history.html', {'page_obj': page_obj})

# 3. Inventory Table
@login_required
def inventory_list(request):
    inventory_items = PS_Inventory.objects.all().order_by('customer_id')
    paginator = Paginator(inventory_items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'inventory_list.html', {'page_obj': page_obj})

# 4. Production Form (already provided, included for completeness)
@login_required
def create_production(request):
    if request.method == 'POST':
        try:
            preform_product_id = request.POST.get('preform_product')
            produced_bottle_product_id = request.POST.get('produced_bottle_product')
            used_preforms = int(request.POST.get('used_materials', 0))
            defective_preforms = int(request.POST.get('defective_materials', 0))
            produced_bottles = int(request.POST.get('produced_units', 0))
            defective_bottles = int(request.POST.get('defective_bottles', 0))
            production_date_str = request.POST.get('production_date', None)
          

            if not all([preform_product_id, produced_bottle_product_id]):
                messages.error(request, "Missing required fields.")
                return redirect('third_party_production_form')

            # ✅ Fetching the preform product from PS_Inventory
            preform_product = get_object_or_404(PS_Inventory, pk=preform_product_id)

            # ✅ Fetching the bottle product from Product (filtered by name for extra safety)
            produced_bottle_product = get_object_or_404(Product, pk=produced_bottle_product_id, name='bottle')
        

            if used_preforms > preform_product.quantity_in_units:
                messages.error(request, "Used materials cannot exceed available inventory.")
                return redirect('third_party_production_form')

            expected_output = produced_bottles + defective_preforms + defective_bottles
            if used_preforms != expected_output:
                messages.error(request, "Sum of produced bottles and defective preforms must equal used preforms.")
                return redirect('third_party_production_form')

            production_date = timezone.now() if not production_date_str else timezone.datetime.strptime(production_date_str, '%Y-%m-%dT%H:%M')

            with transaction.atomic():
                PS_Production.objects.create(
                    preform_product=preform_product,
                    produced_bottle_product=produced_bottle_product,
                    used_preforms=used_preforms,
                    defective_preforms=defective_preforms,
                    produced_bottles=produced_bottles,
                    defective_bottles=defective_bottles,
                    production_date=production_date
                )

            messages.success(request, "Production recorded successfully.")
            return redirect('third_party')
        except Exception as e:
            messages.error(request, f"Error processing request: {e}")
            return redirect('third_party_production_form')

    # ✅ Get preform entries from PS_Inventory
    preforms = PS_Inventory.objects.all()

    # ✅ Get bottles from Product model
    bottles = Product.objects.filter(name='bottle')

    return render(request, 'pd_form.html', {'preforms': preforms, 'bottles': bottles})




def td_dashboard(request):
    # Fetching some data from your models to pass to the template
    productions = PS_Production.objects.all().order_by('-production_date')
    paginator = Paginator(productions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # Returning a response that renders the template 'inventory_dashboard.html'
    return render(request, 'pd_index.html',  {'page_obj': page_obj})

