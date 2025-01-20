from django.shortcuts import render, redirect, get_object_or_404
from .models import Product_type, Color, Supplier, Customer
from django.contrib import messages
# Create your views here.
import random
import string

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password, check_password

def generate_password(length=8):
    """Generate a random alphanumeric password with the specified length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
def generate_username():
    """Generate a username in the format TRV-random_alpha_digits-STF."""
    # Randomly generate a 5-character alphanumeric string
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    # Construct the username
    username = f'TRV-{random_part}-STF'
    return username

def delete_user(request, pk):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return redirect('staff_list')  # Redirect to a list view or another appropriate page
    return redirect('staff_list')


def staff_creation_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        is_superuser = request.POST.get('is_superuser') == 'on'

        # Authenticate the superuser
        if request.user.is_superuser:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists. Please choose a different one.')
                return redirect('staff_creation')  # Redirect back to the form
            
            if password != password2:
                messages.error(request, 'Passwords do not match.')
                return redirect('staff_creation')  # Redirect back to the form

            # Create the user with the provided username and password
            user = User.objects.create_user(username=username, password=password, first_name=name)
            user.is_superuser = is_superuser
            user.save()

            messages.success(request, f'User created: {username}')
            return redirect('staff_list')  # Redirect to staff list after creation
        else:
            messages.error(request, 'You are not authorized to create users.')
            return redirect('staff_creation')  # Redirect back to form if unauthorized

    return render(request, 'staff/staff_creation.html')



def staff_list_view(request):
    users = User.objects.exclude(username=request.user.username)  # Exclude the currently logged-in user
    return render(request, 'staff/staff_list.html', {'users': users})

# from django.contrib.auth.tokens import default_token_generator
# from django.utils.http import urlsafe_base64_encode
# from django.utils.encoding import force_bytes
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.contrib.sites.shortcuts import get_current_site
# from django.urls import reverse

# def  reveal_password_view(request, username):
#     user = User.objects.filter(username=username).first()
#     if user and request.method == 'POST':
#         if request.user.is_superuser:
#             # Generate password reset link
#             token = default_token_generator.make_token(user)
#             uid = urlsafe_base64_encode(force_bytes(user.pk))
#             current_site = get_current_site(request)
#             reset_link = f"{current_site.scheme}://{current_site.get_host()}{reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})}"

#             # Send email with the reset link
#             subject = "Password Reset Requested"
#             message = render_to_string('staff/password_reset_email.html', {
#                 'user': user,
#                 'reset_link': reset_link,
#             })
#             send_mail(subject, message, None, [user.email])

#             messages.success(request, f'Password reset link sent to {user.email}.')
#             return redirect('staff_list')
#         else:
#             messages.error(request, 'You are not authorized to send reset links.')
#     return render(request, 'staff/reveal_password.html', {'username': username})




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
    customer = Customer.objects.all().order_by('name')

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
