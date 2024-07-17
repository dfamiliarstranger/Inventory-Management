from django.shortcuts import render, redirect, get_object_or_404
from .models import Product_type, Color, Supplier, Customer
from django.contrib import messages
# Create your views here.


def product_type_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if not Product_type.objects.filter(name=name).exists():
            Product_type.objects.create(name=name)
            messages.success(request, 'Product type created successfully.')
            return redirect('product_type_list')
        else:
            messages.error(request, 'Product type already exists.')
            return render(request, 'product_type_form.html', {'name': name})
    return render(request, 'product_type/product_type_form.html')


def product_type_list(request):
    product_types = Product_type.objects.all()
    return render(request, 'product_type/index.html', {'product_types': product_types})

# Update View
def product_type_update(request, id):
    product_type = get_object_or_404(Product_type, id=id)
    if request.method == 'POST':
        name = request.POST.get('name')
        if not Product_type.objects.filter(name=name).exclude(id=id).exists():
            product_type.name = name
            product_type.save()
            messages.success(request, 'Product type updated successfully.')
            return redirect('product_type_list')
        else:
            messages.error(request, 'Product type with this name already exists.')
            return render(request, 'product_type/product_type_update.html', {'product_type': product_type})
    return render(request, 'product_type/product_type_update.html', {'product_type': product_type})

# Delete View
def product_type_delete(request, id):
    product_type = get_object_or_404(Product_type, id=id)
    if request.method == 'POST':
        product_type.delete()
        messages.success(request, 'Product type deleted successfully.')
        return redirect('product_type_list')
    return render(request, 'product_type/product_type_confirm_delete.html', {'product_type': product_type})


#COLOR VIEWS
def color_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if not Color.objects.filter(name=name).exists():
            Color.objects.create(name=name)
            messages.success(request, 'Color created successfully.')
            return redirect('color_list')
        else:
            messages.error(request, 'color already exists.')
            return render(request, 'color_form.html', {'name': name})
    return render(request, 'colors/color_form.html')


def color_list(request):
    colors = Color.objects.all()
    return render(request, 'colors/index.html', {'color': colors})

# Update View
def color_update(request, id):
    color = get_object_or_404(Color, id=id)
    if request.method == 'POST':
        name = request.POST.get('name')
        if not Color.objects.filter(name=name).exclude(id=id).exists():
            color.name = name
            color.save()
            messages.success(request, 'Color updated successfully.')
            return redirect('color_list')
        else:
            messages.error(request, 'Color with this name already exists.')
            return render(request, 'colors/color_update.html', {'color': color})
    return render(request, 'colors/color_update.html', {'color': color})

# Delete View
def color_delete(request, id):
    color = get_object_or_404(Color, id=id)
    if request.method == 'POST':
        color.delete()
        messages.success(request, 'Color deleted successfully.')
        return redirect('color_list')
    return render(request, 'colors/color_confirm_delete.html', {'color': color})





#SUPPLIER VIEWS
def supplier_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        mobile_1 = request.POST.get('mobile_1')
        mobile_2 = request.POST.get('mobile_2')
        email = request.POST.get('email')
        contact_info = request.POST.get('contact_info')
        
        if not Supplier.objects.filter(name=name).exists():
            Supplier.objects.create(name=name, mobile_1=mobile_1, mobile_2=mobile_2, email=email, contact_info=contact_info)
            messages.success(request, 'Supplier created successfully.')
            return redirect('supplier_list')
        else:
            messages.error(request, 'Supplier already exists.')
            return render(request, 'suppliers/supplier_form.html', {'name': name, 'mobile_1': mobile_1, 'mobile_2': mobile_2, 'email': email, 'contact_info': contact_info})
    return render(request, 'suppliers/supplier_form.html')


def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'suppliers/index.html', {'suppliers': suppliers})


def supplier_update(request, id):
    supplier = get_object_or_404(Supplier, id=id)
    if request.method == 'POST':
        name = request.POST.get('name')
        mobile_1 = request.POST.get('mobile_1')
        mobile_2 = request.POST.get('mobile_2')
        email = request.POST.get('email')
        contact_info = request.POST.get('contact_info')
        
        if not Supplier.objects.filter(name=name).exclude(id=id).exists():
            supplier.name = name
            supplier.mobile_1 = mobile_1
            supplier.mobile_2 = mobile_2
            supplier.email = email
            supplier.contact_info = contact_info
            supplier.save()
            messages.success(request, 'Supplier updated successfully.')
            return redirect('supplier_list')
        else:
            messages.error(request, 'Supplier with this name already exists.')
            return render(request, 'suppliers/supplier_update.html', {'supplier': supplier})
    return render(request, 'suppliers/supplier_update.html', {'supplier': supplier})


def supplier_delete(request, id):
    supplier = get_object_or_404(Supplier, id=id)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Supplier deleted successfully.')
        return redirect('supplier_list')
    return render(request, 'suppliers/supplier_confirm_delete.html', {'supplier': supplier})





#CUSTOMER VIEWS
def customer_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        mobile_1 = request.POST.get('mobile_1')
        mobile_2 = request.POST.get('mobile_2')
        email = request.POST.get('email')
        contact_info = request.POST.get('contact_info')
        
        if not Customer.objects.filter(name=name).exists():
            Customer.objects.create(name=name, mobile_1=mobile_1, mobile_2=mobile_2, email=email, contact_info=contact_info)
            messages.success(request, 'Customer created successfully.')
            return redirect('customer_list')
        else:
            messages.error(request, 'Customer already exists.')
            return render(request, 'customer/customer_form.html', {'name': name, 'mobile_1': mobile_1, 'mobile_2': mobile_2, 'email': email, 'contact_info': contact_info})
    return render(request, 'customer/customer_form.html')


def customer_list(request):
    customer = Customer.objects.all()
    return render(request, 'customer/index.html', {'customer': customer})


def customer_update(request, id):
    customer = get_object_or_404(Customer, id=id)
    if request.method == 'POST':
        name = request.POST.get('name')
        mobile_1 = request.POST.get('mobile_1')
        mobile_2 = request.POST.get('mobile_2')
        email = request.POST.get('email')
        contact_info = request.POST.get('contact_info')
        
        if not Supplier.objects.filter(name=name).exclude(id=id).exists():
            customer.name = name
            customer.mobile_1 = mobile_1
            customer.mobile_2 = mobile_2
            customer.email = email
            customer.contact_info = contact_info
            customer.save()
            messages.success(request, 'Customer updated successfully.')
            return redirect('supplier_list')
        else:
            messages.error(request, 'Customer with this name already exists.')
            return render(request, 'customer/customer_update.html', {'customer':customer})
    return render(request, 'customer/customer_update.html', {'customer':customer})


def customer_delete(request, id):
    customer = get_object_or_404(Customer, id=id)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully.')
        return redirect('customer_list')
    return render(request, 'customer/customer_confirm_delete.html', {'customer': customer})
