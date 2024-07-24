from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.contrib import messages
from .models import Production
from purchase.models import Inventory
from product.models import Product
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

@login_required
def create_production(request):
    if request.method == 'POST':
        try:
            preform_product_id = request.POST.get('preform_product')
            produced_bottle_product_id = request.POST.get('produced_bottle_product')
            used_preforms = int(request.POST.get('used_preforms', 0))
            defective_preforms = int(request.POST.get('defective_preforms', 0))
            produced_bottles = int(request.POST.get('produced_bottles', 0))
            defective_bottles = int(request.POST.get('defective_bottles', 0))
            production_date_str = request.POST.get('production_date', None)

            if not all([preform_product_id, produced_bottle_product_id]):
                messages.error(request, "Missing required fields.")
                return redirect('production_form')

            try:
                preform_product = Inventory.objects.get(pk=preform_product_id)
                produced_bottle_product = Product.objects.get(pk=produced_bottle_product_id)
            except Inventory.DoesNotExist:
                messages.error(request, "Preform product not found.")
                return redirect('production_form')
            except Product.DoesNotExist:
                messages.error(request, "Produced bottle product not found.")
                return redirect('production_form')

            # Check if used preforms are more than available in inventory
            if used_preforms > preform_product.unit:
                messages.error(request, "Used preforms cannot exceed available inventory.")
                return redirect('production_form')

            # Check if used preforms equals the sum of produced bottles, defective bottles, and defective preforms
            if used_preforms != (produced_bottles + defective_bottles + defective_preforms):
                messages.error(request, "The sum of produced bottles, defective bottles, and defective preforms must equal the used preforms.")
                return redirect('production_form')
            # Parse the production date, if provided
            if production_date_str:
                try:
                    production_date = timezone.datetime.strptime(production_date_str, '%Y-%m-%dT%H:%M')
                except ValueError:
                    messages.error(request, "Invalid date format. Please use the correct format.")
                    return redirect('production_form')
            else:
                production_date = timezone.now()

            with transaction.atomic():
                production = Production(
                    preform_product=preform_product,
                    produced_bottle_product=produced_bottle_product,
                    used_preforms=used_preforms,
                    defective_preforms=defective_preforms,
                    produced_bottles=produced_bottles,
                    defective_bottles=defective_bottles,
                    production_date=production_date
                )
                production.save()
               

            messages.success(request, "Production created successfully.")
            return redirect('production_list')

        except (Inventory.DoesNotExist, Product.DoesNotExist, ValueError) as e:
            messages.error(request, f"Error processing the request: {str(e)}")
            return redirect('production_form')

    # Query for preforms and bottles to populate the dropdowns
    preforms = Inventory.objects.filter(product__name='preform')
    bottles = Product.objects.filter(name='bottle')

    # Provide context to the template
    context = {
        'preforms': preforms,
        'bottles': bottles,
    }
    return render(request, 'production_form.html', context)



@login_required
def production_list(request):
    productions = Production.objects.all().order_by('production_date')

    paginator = Paginator(productions, 10)  # Paginate with 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'production_list.html', {'page_obj': page_obj})




@login_required
def production_delete(request, pk):
    production = get_object_or_404(Production, pk=pk)

    if request.method == 'POST':
        production.delete()
        messages.success(request, 'Production deleted and inventory reverted successfully.')
        return redirect('production_list')

    return redirect('production_list')
