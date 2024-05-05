from django.shortcuts import render, redirect
from .models import Cap, Preform, Preform_type, Supplier, Customer, StockItem, update_inventory, Production, Stock, Sales
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout 
from django.contrib import messages
from .forms import CapForm, PreformForm, CustomerForm, SupplierForm, StockItemForm, ProductionForm
from django.utils import timezone
from django.http import HttpResponse
from django.db import transaction
from django.db.models import F
###############     Create your views here    ###############

@login_required
def home(request):
    return render(request, ('base/home.html'))

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'base/login.html', {'error_message':'invalid username or password'})
    return render(request, 'base/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

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
def preform(request):
    preform = Preform.objects.all()
    return render(request, ('products/preform/index.html'), {'preforms':preform})

@login_required
def preform_type(request):
    preform_type = Preform_type.objects.all()
    return render(request, ('products/cap/index.html'), {'preform_types':preform_type})

@login_required
def create_preform(request):
    if request.method == "POST":
        form = PreformForm(request.POST)
        if form.is_valid():
           form.save()
           return redirect('preform')
        else:
            return redirect('create_preform')
    else:
        form = PreformForm()
        preform_type = Preform_type.objects.all()
    return render(request, 'products/preform/form.html', {'form':form, 'preform_types':preform_type})

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
    return render(request, 'clients/customer/index.html', {'customers':customer})

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
            
            return redirect('stock') 
        else:
            print(form.errors)
            return redirect('add_stock')
    else:
        return render(request, 'store/add_stock/index.html', {'stock_form': stock_form, 'preform_types': preform_type, 'caps': cap, 'suppliers': supplier})


@login_required
def purchase_history(request):
    stock = StockItem.objects.all()
    return render(request, 'store/add_stock/details.html', {'stocks': stock })

# @login_required
# def stock_detail(request):
#     stock_item = Stock.objects.all()
#     return render(request, 'stock/index.html', {'stock_item': stock_item })

@login_required
def stock_detail(request):
    # Get all stock items
    updated_stock_items = Stock.objects.all()

    # Iterate through each stock item
    for updated_stock_item in updated_stock_items:
        # If the stock quantity is zero, delete the stock record
        if updated_stock_item.quantity == 0:
            updated_stock_item.delete()

    # Retrieve the updated stock items after deletion
    stock_items = Stock.objects.all()

    return render(request, 'stock/index.html', {'stock_item': stock_items})


#####################                     PRODUCTION                          ######################


# @login_required
# def production(request):
#     stock = Stock.objects.filter(name='Preform')
#     if request.method == "POST":
#         form = ProductionForm(request.POST)
#         if form.is_valid():
#            form.save()
#            return redirect('record')
#         else:
#             return redirect('production')
#     else:
#         form = ProductionForm()
#     return render(request, 'production/index.html', {'stock': stock})


@login_required
def production(request):
    if request.method == 'POST':
        # Get form data
        product_id = request.POST.get('product')
        product_quantity = request.POST.get('preform_quantity')
        shortages = request.POST.get('shortages')
        excesses = request.POST.get('excesses')
        damages = request.POST.get('damages')
        waste_bottle = request.POST.get('waste_bottle')
        good_bottle = request.POST.get('good_bottle')
        bottle_size = request.POST.get('bottle_size')
        bottle_color = request.POST.get('color')

        # Perform input validation
        if not product_id or not product_quantity or not bottle_color or not good_bottle:
            messages.error(request, 'Please fill all required fields.')
            return redirect('production')

        # Perform business logic checks
        try:
            product_quantity = int(product_quantity)
            waste_bottle = int(waste_bottle)
            good_bottle = int(good_bottle)
            bottle_size = int(bottle_size)
        except ValueError:
            messages.error(request, 'Quantity fields must be integers.')
            return redirect('production')

        product = Stock.objects.get(pk=product_id)

        # Check if there's enough preform quantity
        if product.quantity < product_quantity:
            messages.error(request, 'Insufficient stock quantity.')
            return redirect('production')
        
        try:
            # Start a database transaction
            with transaction.atomic():
                # Deduct product quantity used from stock
                product.quantity -= product_quantity
                product.save()

                # Create Production object
                production_instance = Production.objects.create(
                    product=product,
                    product_quantity=product_quantity,
                    shortages=shortages,
                    excesses=excesses,
                    damages=damages,
                    waste_bottle=waste_bottle,
                    good_bottle=good_bottle,
                    bottle_size=bottle_size,
                    bottle_color=bottle_color
                )

                # Create Bottle Stock
                bottle_stock, created = Stock.objects.get_or_create(
                    name='Bottle',
                    color=bottle_color,
                    product_type='Bottle',
                    quantity=good_bottle
                )

                messages.success(request, 'Production record created successfully.')
                return redirect('record')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('production')

    else:
        stock = Stock.objects.all()
        return render(request, 'production/index.html', {'stock': stock})

@login_required
def production_record(request):
    record = Production.objects.all()
    return render(request, 'production//summary.html', {'record': record })

@login_required
def sales_record(request):
    sales = Sales.objects.all()
    return render(request, 'sales/index.html', {'sale': sales })

@login_required
def sales_form(request):
    if request.method == 'POST':
        # Get form data
        product_id = request.POST.get('product_id')
        customer_id = request.POST.get('customer_id')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')

        # Perform input validation
        if not product_id or not customer_id or not quantity or not price:
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
    

        # Convert product.quantity to integer before comparison
        if int(product.quantity) < int(quantity):
            messages.error(request, 'Insufficient stock quantity.')
            return redirect('sales_form')

        # Calculate total
        total = quantity * price

        # Create Sales object
        sale = Sales.objects.create(
            product=product,
            customer_id=customer_id,
            quantity=quantity,
            price=price,
            total=total
        )

        # Update stock quantity
        product.quantity -= quantity
        product.save()

        messages.success(request, 'Sale completed successfully.')
        return redirect('sales_record')

    else:
        
        stock = Stock.objects.all()
        customer = Customer.objects.all()
        sales = Sales.objects.all()
        return render(request, 'sales/forms.html', {'sales': sales, 'stock':stock, 'customer':customer })