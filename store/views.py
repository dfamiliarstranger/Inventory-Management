from django.shortcuts import render, redirect
from .models import Cap, Preform, Preform_type, Supplier, Customer, StockItem, update_inventory, Production, Stock
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout 
from .forms import CapForm, PreformForm, CustomerForm, SupplierForm, StockItemForm, ProductionForm
from django.utils import timezone
from django.http import HttpResponse

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
# def add_stock_item(request):
#     stock_form = StockItemForm()
#     preform_type = Preform_type.objects.all()
#     cap = Cap.objects.all()
#     supplier = Supplier.objects.all()
#     if request.method == 'POST':
        
#         form = StockItemForm(request.POST)
#         print(request.POST)
#         if form.is_valid():
#            form.save()
#            return redirect('stock')
#         else:
#             print(form.errors)
#             return redirect('add_stock')
#     else:
#        return render(request, 'store/add_stock/index.html', {'stock_form': stock_form, 'preform_types':preform_type, 'caps':cap, 'suppliers':supplier})
def add_stock_item(request):
    stock_form = StockItemForm()
    preform_type = Preform_type.objects.all()
    cap = Cap.objects.all()
    supplier = Supplier.objects.all()
    
    if request.method == 'POST':
        form = StockItemForm(request.POST)
        if form.is_valid():
            # Extracting data from the form
            name = request.POST.get('name', '')  # Assuming product_type is a select field in the form
            color = request.POST.get('color', '')  # Assuming color is a char field in the form
            quantity = request.POST.get('quantity', '')  # Assuming quantity is a char field in the form
            supplier_id = request.POST.get('supplier', '')  # Assuming supplier is a select field in the form
            cap_type_id = request.POST.get('cap_type', '')  # Assuming cap_type is a select field in the form
            preform_type_id = request.POST.get('preform_type', '')  # Assuming preform_type is a select field in the form
            product_type = request.POST.get('product_type', '')  # Assuming preform_type is a select field in the form
            price = request.POST.get('price', '')  # Assuming price is a decimal field in the form
            total = request.POST.get('total', '')  # Assuming price is a decimal field in the form
            
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

@login_required
def stock_detail(request):
    stock_item = Stock.objects.all()
    return render(request, 'stock/index.html', {'stock_item': stock_item })


#####################                     PRODUCTION                          ######################
@login_required
def production(request):
    stock = Stock.objects.filter(name='Preform')
    if request.method == "POST":
        form = ProductionForm(request.POST)
        if form.is_valid():
           form.save()
           return redirect('record')
        else:
            return redirect('production')
    else:
        form = ProductionForm()
    return render(request, 'production//index.html', {'stock': stock})


@login_required
def production_record(request):
    record = Production.objects.all()
    return render(request, 'production//summary.html', {'record': record })